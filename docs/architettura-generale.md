# Architettura generale

Documento madre del progetto: dice cosa realizziamo, con quali componenti e quali decisioni sono
già prese. Da qui nascono i file per componente (`docs/<componente>.md`) e poi i ticket.

Stato: **bozza del 2026-11-24**, da far approvare al professore prima di scrivere i file per
componente.

Legenda: **[deciso]** confermato dal team · **[proposta]** scelta nostra non ancora confermata ·
**[aperto]** da chiudere, con la prova o il ticket che lo chiude.

## 1. Cosa realizziamo

Una pagina web in forma di chat. L'utente scrive in italiano naturale, formule dettate a parole
comprese (per esempio «integrale da zero a infinito di e alla meno x quadro dx»), e ottiene un
documento PDF LaTeX. Chi scrive deve conoscere l'italiano, non LaTeX.

Accanto alla chat c'è un pannello per governare il modello e il documento. Quindi la pagina fa:

- **Chat**: casella per il testo da inviare e storico dei messaggi della sessione.
- **Controlli del modello**: selettore del backend (API oppure locale), indicatore «modello
  occupato» che blocca l'invio finché il modello non è libero, annulla la richiesta in corso e
  rigenera l'ultima. **[deciso]**
- **Documento**: anteprima del PDF compilato, download del PDF e visualizzazione e download del
  sorgente `.tex`. **[deciso]**

Uso locale, un utente alla volta, senza login. **[deciso]**

Il PDF viene compilato dal container del compilatore, arriva alla pipeline e la pipeline lo
passa alla pagina.

## 2. Vincoli del corso

Criteri del professore (riferimento: `UNICT-Quality-Development/qd-starter-pack`) e come li
rispettiamo:

| Criterio | Come |
|---|---|
| git e Conventional Commits | in uso; regole in `AGENTS.md` |
| ogni modifica a `main` con PR revisionata da almeno un membro | protezione del branch `main`, 1 approvazione |
| pipeline con linter, type checker, formatter e test | ruff e ty, file `lint.yml` e `test.yml` |
| unit test con pytest, coverage almeno 90% | `fail_under = 90` in `pyproject.toml`, verificato dalla pipeline |
| test E2E con Playwright eseguiti nella pipeline | **da fare** (sezione 10) |
| Dockerfile e workflow che pubblica un'immagine su ghcr.io | Dockerfile di `web` presente; workflow **da fare** (sezione 10) |
| `AGENTS.md` e flusso di lavoro moderno | `AGENTS.md` e le skill condivise in `agent-skills/` |
| README chiaro; codice, commenti e commit in inglese | README in italiano per scelta del team; codice, commenti, branch e commit in inglese |

## 3. Componenti

Ogni componente ha la sua cartella, con dentro i suoi test, e un container Docker. Quelle in Python
hanno il loro `pyproject.toml` (workspace uv); `web` è un progetto npm autonomo. Un file
`docker-compose` avvia l'insieme. **[proposta]**

```
 browser ──HTTP──► web ──HTTP──► pipeline ──HTTP──► compiler
                  (pagina)         │   │            (TeX Live, senza rete)
                                   │   └──HTTPS──► API OpenAI
                                   └──HTTP──► ollama (modello locale)
```

| Componente | Cosa fa | Cosa non fa |
|---|---|---|
| `web` | serve la pagina chat; inoltra le richieste del browser alla pipeline e le risposte al browser | non converte, non valida, non compila; non parla né con l'LLM né con il compilatore |
| `pipeline` | segmenta il testo, chiede la conversione all'LLM un blocco alla volta, valida, assembla il `.tex`, lo manda al compilatore, tiene lo stato del job | non serve la pagina; non compila |
| `compiler` | compila il `.tex` in un ambiente isolato e restituisce il PDF o l'errore | non conosce né la pagina né l'LLM; non ha rete |
| `ollama` | server del modello locale (immagine ufficiale `ollama/ollama`) | nessun codice nostro |

`llm` non è un container nostro: è un modulo della pipeline (il client verso il modello, sezione
6) più il container `ollama`. Resta comunque un file `docs/llm.md`, perché è un punto di
progettazione a sé. **[deciso]**

Reti Docker **[proposta]**: `web` raggiunge solo la pipeline; la pipeline raggiunge `compiler`,
`ollama` e, solo per il backend API, internet in uscita; `compiler` sta in una rete interna senza
accesso a internet.

## 4. Flusso di una richiesta

1. L'utente scrive il testo, sceglie il backend e preme invio. Se il modello è occupato, l'invio è
   bloccato.
2. La pagina manda il testo alla pipeline (tramite `web`). La pipeline risponde subito con un
   identificativo di job: la richiesta è asincrona.
3. La pipeline **segmenta** il testo in blocchi (paragrafi, titoli, elenchi).
4. Per ogni blocco chiede la conversione all'LLM, **valida** la risposta e passa il frammento
   LaTeX al passo successivo. Un blocco che fallisce diventa un avviso nel documento.
5. La pipeline **assembla** i frammenti nel preambolo fisso e ottiene il `.tex`.
6. La pipeline manda il `.tex` al compilatore, che restituisce il PDF.
7. La pagina riceve lo stato durante tutto il percorso (in coda, blocco 3 di 9, compilazione,
   finito) e alla fine mostra l'anteprima e abilita i download di PDF e `.tex`.

Esito di un job **[proposta]**: *riuscito*; *riuscito con avvisi* (PDF prodotto, con il numero
dei blocchi non convertiti); *fallito*, con una causa tra: modello non disponibile, compilazione
fallita, testo vuoto o troppo lungo, tempo scaduto, annullato dall'utente.

## 5. Interfacce tra i componenti

Dettaglio dei contratti nei file per componente. Qui le scelte di fondo.

### 5.1 Pagina e pipeline **[deciso]**

HTTP; lo stato dei job arriva alla pagina con **Server-Sent Events** (SSE), senza WebSocket né
polling. Un job alla volta. Forma indicativa **[proposta]**:

| Richiesta | Scopo |
|---|---|
| `GET /api/status` | modello libero o occupato, backend disponibili, test mode acceso o no |
| `POST /api/jobs` | nuovo job: testo e backend; `202` con l'id, `409` se il modello è occupato |
| `GET /api/jobs/{id}/events` | flusso SSE con lo stato e il progresso per blocco |
| `DELETE /api/jobs/{id}` | annulla: si ferma tra un blocco e l'altro e interrompe la chiamata in corso |
| `GET /api/jobs/{id}/pdf`, `GET /api/jobs/{id}/tex` | anteprima e download |

«Rigenera» è un nuovo job con lo stesso testo.

### 5.2 Pipeline e compilatore **[deciso]**

Un **servizio HTTP sempre acceso**: la pipeline invia il `.tex`, riceve il PDF oppure l'errore del
compilatore. Niente container creato a ogni richiesta, perché richiederebbe alla pipeline l'accesso
al socket Docker, che è un rischio maggiore di quello che evitiamo.

### 5.3 Pipeline e LLM

Vedi sezione 6.

## 6. LLM

### 6.1 Decisioni **[deciso]**

- Il client sta **dentro la pipeline**, dietro un'unica interfaccia (`LlmClient`). Nessun
  container `llm`.
- L'LLM produce **solo il corpo del documento**, blocco per blocco, in **JSON con schema**. Il
  preambolo è fisso e non lo vede né lo modifica.
- Il modello locale gira in **un container `ollama`** con l'immagine ufficiale, con i modelli in un
  volume.
- Per l'API esterna si usa l'SDK ufficiale `openai` (dipendenza approvata dal team, da aggiungere
  quando c'è il codice).
- Un blocco non valido diventa un avviso nel documento; niente repair loop per ora.
- **LLM finto** (6.3) per test e sviluppo.

### 6.2 Cosa sappiamo dagli esperimenti

Dalla repo di prova (privata), con Ollama nativo su Mac 8 GB, `qwen2.5:3b`, temperatura 0,
9 esempi del dataset, controlli attuali (numeri indicativi, non una valutazione):

- 8 risposte su 9 valide e 5 su 9 identiche all'atteso con il prompt `v2`.
- Su un secondo testo di 9 blocchi (prompt `v1`) tutto compila su Overleaf, ma 4 blocchi hanno
  contenuto sbagliato: compilare non vuol dire essere corretti.
- Il client attuale parla il protocollo **nativo** di Ollama (`/api/chat`, schema nel campo
  `format`) con opzioni per richiesta (`num_ctx`, `num_gpu`, `num_thread`, `keep_alive`) che
  servono su macchine Windows con GPU.

### 6.3 LLM finto e test mode **[deciso]**

- Restituisce, per ogni blocco, **un frammento LaTeX fisso scelto dal team**, uno per tipo di
  blocco (`paragraph`, `heading`, `list`, `display_math`), dentro un JSON valido con il `block_id`
  della richiesta. Passa quindi per tutta la validazione vera.
- Si accende solo con una variabile d'ambiente interna, **non ha una voce nel selettore**: nella
  pagina compare come backend «locale».
- Per non scambiarlo per un modello vero: all'avvio la pipeline scrive nel log
  `FAKE LLM ACTIVE`, `GET /api/status` espone `test_mode`, e la pagina mostra un badge
  **«test mode»**.
- Serve a: unit test della pipeline senza dipendere da un modello, E2E Playwright nella CI,
  sviluppo di `web` e `compiler` prima che la pipeline sia completa.

### 6.4 Domande aperte sull'LLM

| # | Domanda | Perché conta | Come si chiude |
|---|---|---|---|
| L1 | **Un client solo** (SDK `openai`, anche verso Ollama dall'ingresso `/v1`) **o due** (`OllamaClient` nativo e `OpenAIClient`)? | Un client solo è meno codice; due classi tengono le opzioni per richiesta e il codice già collaudato | prova in L2, poi si sceglie |
| L2 | Ollama dall'ingresso `/v1` rispetta lo **schema JSON** dei blocchi, e dà la stessa qualità di oggi con `qwen2.5:3b`? E OpenAI lo accetta in modalità stretta (limiti numerici di `confidence`, campi obbligatori)? | Se lo schema non passa, il client unico non funziona | prova: container `ollama` con `qwen2.5:3b`, un blocco vero da entrambi gli ingressi, confronto di validità e tempi |
| L3 | Dove si fissano `num_ctx`, `num_gpu`, `num_thread`, `keep_alive` quando Ollama è in container? | Con `/v1` non passano per richiesta: vanno nel server (variabili del container, Modelfile, `gpus` nel compose) | stessa prova; si documenta in `docs/llm.md` |
| L4 | **`qwen2.5:3b` basta** per la demo? Serve un modello più grande? Quale modello OpenAI offre il backend API? | Qualità e tempi della demo; nei test di prova sbaglia ancora formule difficili (binomiali, simboli) | misura sullo stesso dataset con i candidati; scelta del team |
| L5 | **Dove gira il server della demo**, con quale hardware? | Su Mac Docker non vede la GPU: il modello in container gira solo su CPU, più lento. Su Windows con GPU NVIDIA (WSL2) e su Linux con NVIDIA Container Toolkit sì | decisione del team; tempi misurati nella prova L2 |
| L6 | Il **prompt `v2`** è tarato su `qwen2.5:3b`: con un modello OpenAI va rivalutato? | Ogni modifica a prompt ed esempi va confrontata con una baseline | confronto sullo stesso dataset quando c'è il client API |
| L7 | **Annullare** una richiesta in corso interrompe davvero la generazione su Ollama e su OpenAI? | L'annulla della pagina deve liberare il modello | verifica nella prova L2: chiusura della connessione a metà richiesta |
| L8 | **Chiave API**: dove la teniamo? | Mai nell'immagine, nel repo o nei log | variabile d'ambiente o secret di Docker; regola in `docs/llm.md` |
| L9 | Il modello (circa 2 GB) si scarica **al primo avvio**: chi lo scarica e dove? | Primo avvio lento; in CI non serve (usa il finto) | volume del container `ollama` e comando documentato |

## 7. Pipeline

Fonte: la pipeline già sperimentata nella repo di prova, che porteremo qui **un pezzo alla volta**,
ognuno con i suoi test, sotto lint, tipi e coverage (il piano di passaggio si scrive dopo
l'approvazione).

- **Segmentazione**: riga vuota = separatore; riga `#`, `##`, `###` = titolo; righe `-` o `1.`
  consecutive = elenco; il resto è paragrafo. Ogni blocco ha un identificativo stabile (hash del
  contenuto).
- **Tipi di blocco in uscita**: `paragraph`, `heading`, `display_math` (l'LLM può trasformare un
  paragrafo in formula isolata), `list`.
- **Contratto con l'LLM**: per ogni blocco entra il testo italiano e il tipo; esce un JSON con
  `block_id`, `block_type`, `latex` (solo il corpo), `confidence`, `ambiguities`, `notes`.
  Lo schema si valida in Python.
- **Prompt**: file versionati, mai sparsi nel codice; esempi few-shot in un file separato.
- **Controlli, in quest'ordine, il primo che fallisce decide il motivo**: blocco troppo lungo
  (oltre 3000 caratteri, non viene inviato); errore o timeout dell'LLM; JSON non valido o
  `block_id` diverso; comando vietato; caratteri di controllo (backslash non raddoppiata);
  graffe non bilanciate; comandi matematici fuori dal modo matematico. Prima dei controlli, i
  simboli Unicode matematici e greci sono tradotti in comandi LaTeX con una tabella fissa.
- **Errori**: un blocco che fallisce diventa un avviso nel documento («Blocco … non convertito:
  riscrivi questo passaggio in modo più chiaro»), il resto del documento si produce. Se il modello
  non è raggiungibile l'intero job si ferma. Se la **compilazione** fallisce, il job fallisce e la
  pagina mostra l'errore; l'utente usa «rigenera». Nessun ciclo di riparazione. **[deciso]**
- **Template fisso** con segnaposto per il corpo: `article`, `babel` italiano, `amsmath`,
  `amssymb`, `amsthm`. Non si genera né si modifica a runtime.
- **Un job alla volta**: la pipeline tiene il blocco «modello occupato»; il progresso per blocco
  alimenta il flusso SSE e i punti di annullamento. **[proposta]**

Da costruire sopra il codice esistente: l'API HTTP, il gestore dei job (occupato, annulla, SSE) e
il client verso il compilatore.

## 8. Compilatore e sicurezza

Il LaTeX prodotto da un LLM è **non attendibile**, e così il testo dell'utente.

| Chi o cosa | Rischio | Difesa |
|---|---|---|
| Testo dell'utente | comandi LaTeX o istruzioni per il modello | il modello vede solo il blocco; l'output passa dai controlli |
| Output dell'LLM | `\write18`, `\input` di file, `\openout`, ridefinizioni | elenco di comandi vietati rifiutato prima dell'assemblaggio; preambolo fisso |
| Il `.tex` | lettura o scrittura di file dell'host, comandi, rete | compilazione solo nel container `compiler` |
| Server LLM | esposizione sulla rete | `ollama` raggiungibile solo dalla pipeline |

Il container `compiler` **[deciso come obiettivo, da realizzare e testare]**: nessuna rete,
filesystem in sola lettura tranne una cartella temporanea per compilazione, utente non
privilegiato, timeout, limiti di CPU e memoria, niente shell-escape. Test che dimostrino che
`\write18`, `\input` di file dell'host e l'accesso alla rete falliscono.

## 9. Pagina web

- Serve la chat e il pannello dei controlli; mostra l'anteprima del PDF e i download.
- Stato dei job via SSE; indicatore «modello occupato»; annulla e rigenera.
- Badge «test mode» quando la pipeline è in modalità test.
- React e TypeScript, serviti da nginx, che inoltra `/api/*` alla pipeline. **[deciso]** Dettagli in
  `docs/web.md`.

## 10. Qualità e test

- **Unit test** con coverage almeno al 90%: pytest per il codice Python, già nella CI; Vitest per
  `web`, non ancora nella CI. Che Vitest soddisfi il criterio del corso è **[aperto]**. Ogni script
  ha i suoi test. La pipeline si prova con il client finto, nessun test dipende da un modello.
- **E2E con Playwright** nella CI, con il sistema avviato dal compose e il client finto acceso:
  scrivi un testo, vedi lo stato, vedi l'anteprima, scarichi PDF e `.tex`; modello occupato e
  annulla. I passi sono in `docs/web-piano.md`. **[proposta]**
- **Immagini Docker su ghcr.io**: un `Dockerfile` per ogni componente nostro e un workflow di
  pubblicazione. I passi sono in `docs/web-piano.md`. **[proposta]**

## 11. Altre domande aperte

| # | Domanda | Come si chiude |
|---|---|---|
| A3 | Motore del compilatore: `pdflatex` (come Overleaf) o `tectonic`? | prova nel container; `docs/compiler.md` |
| A4 | Cosa conserva la pipeline e per quanto (testo, `.tex`, PDF dell'ultimo job)? | `docs/pipeline.md`; proposta: solo l'ultimo risultato, in memoria o in cartella temporanea |
| A5 | Quando si pubblicano le immagini: a ogni merge su `main` o su tag? | workflow `docker.yml` |
| A6 | Forma esatta dell'API e degli eventi SSE | `docs/pipeline.md` |

## 12. Passi successivi

1. Far approvare questo documento dal professore.
2. Prova su `ollama` in container (domande L1–L3 e L7): prima cosa da fare, perché sblocca la scelta
   del client.
3. Interfaccia `LlmClient` e LLM finto, con test.
4. File per componente: `docs/web.md`, `docs/pipeline.md`, `docs/llm.md`, `docs/compiler.md`.
5. Piano di passaggio della pipeline dalla repo di prova, poi ticket piccoli, uno per task.
