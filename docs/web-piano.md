# Piano di lavoro: `web`

Passi per realizzare la componente `web`, divisi in task piccoli e isolati per tenere le PR facili da
revisionare. Le regole di lavoro stanno in `AGENTS.md`, il quadro d'insieme in
`docs/architettura-generale.md`.

Stato: **bozza**. La fase 2 va rivista dopo aver esaminato il mockup HTML.

**Dove siamo:** fatti i task da 1.1 a 1.3. Il prossimo è l'1.4, dopo il merge del container.

## Come si legge

- Un task = un branch = una PR. Il titolo della PR è indicato sotto ogni task.
- I task si fanno nell'ordine scritto; ognuno parte da `main` aggiornato, dopo il merge di quelli da
  cui dipende.
- Ogni task con del codice include i suoi **unit test** (regola di `AGENTS.md`).
- Un task è finito quando vale quanto scritto in «Finito quando» e i controlli esistenti passano.
- Se durante il lavoro un task risulta troppo grande, si divide e si aggiorna questo file.

Stack e container sono descritti in `docs/web.md`. In più, gli end-to-end si scrivono con
Playwright in TypeScript.

## Fase 1: container con configurazione base

### 1.1, 1.2 e 1.3 Stack, container nginx e progetto React (fatti)

- **PR:** `feat(web): add react app served by an nginx container`, branch `feat/web-react-container`
- **Eccezione:** erano tre task, riuniti in una sola PR per arrivare subito a una pagina React in un
  container. La stessa PR porta questo piano, la regola «Spiegare il lavoro» di `AGENTS.md` e la
  rimozione dell'handoff.
- **Contenuto:** `docs/web.md` e regole per npm e Vitest; pagina React bianca con i suoi unit test;
  `Dockerfile` in due fasi (build con Node, poi nginx). Ogni componente tiene i test nella sua
  cartella: quelli di `web` sono in `web/tests/`.
- **Per la revisione:** `package-lock.json` è generato da npm, è lungo e non si legge riga per riga.

### 1.4 Controlli sulla PR

- **PR:** `chore(web): run web checks on pull requests`, branch `chore/web-ci-checks`
- **Contenuto:** GitHub Action con unit test, coverage, controllo dei tipi, lint e formattazione di
  `web`. Gli strumenti di lint e formattazione si scelgono qui (sono dipendenze da approvare),
  verificando che funzionino con TypeScript 7. I comandi partono da `web/`. Un controllo
  obbligatorio non va filtrato per cartella a livello di workflow: quando il workflow viene saltato,
  il controllo resta in attesa e blocca il merge.
- **Finito quando:** un test che fallisce rende rossa la PR. L'admin aggiunge poi il nuovo controllo
  a quelli obbligatori nella protezione di `main`.
- **Dipende da:** merge dei task da 1.1 a 1.3

Sta nella fase 1 perché, fino a questo task, i test di `web` non impediscono il merge.

## Fase 2: scheletro della pagina

Pagina **statica**: si vede la disposizione, ma i controlli non fanno niente e non ci sono chiamate
di rete. La divisione segue la specifica e va confrontata con il mockup.

| Task | Branch e titolo della PR | Contenuto | Finito quando |
|---|---|---|---|
| 2.1 Layout | `feat/web-page-layout`<br>`feat(web): add page layout` | struttura della pagina, con le aree per chat, controlli del modello e documento, e stili di base | le aree sono disposte come nel mockup |
| 2.2 Chat | `feat/web-chat-skeleton`<br>`feat(web): add static chat area` | storico vuoto, casella di testo, pulsante di invio | gli elementi si vedono e hanno un unit test |
| 2.3 Controlli | `feat/web-controls-skeleton`<br>`feat(web): add static model controls` | selettore del backend, indicatore di stato, «annulla», «rigenera» | come sopra |
| 2.4 Documento | `feat/web-document-skeleton`<br>`feat(web): add static document panel` | spazio per l'anteprima, download di PDF e `.tex`, vista del sorgente | come sopra |

La 2.1 dipende dalla fase 1. Le altre tre dipendono dalla 2.1 e sono indipendenti tra loro.

## Fase 3: end-to-end e pubblicazione

Gli unit test arrivano già con ogni task. Questa fase aggiunge ciò che prova il container intero.

| Task | Branch e titolo della PR | Contenuto | Finito quando |
|---|---|---|---|
| 3.1 Playwright | `test/web-playwright-setup`<br>`test(web): add playwright smoke test` | configurazione di Playwright (dipendenza `@playwright/test`) e un primo test in `web/tests/e2e/` sullo scheletro | il test passa in locale contro il container e il comando è in `AGENTS.md` |
| 3.2 E2E nella CI | `chore/web-e2e-ci`<br>`chore(web): run e2e tests in ci` | Action che costruisce il container ed esegue gli end-to-end; regola aggiornata in `AGENTS.md` | gli end-to-end partono sulla PR |
| 3.3 Immagine | `chore/web-publish-image`<br>`chore(web): publish web image to ghcr` | workflow che pubblica l'immagine su ghcr.io; si decide se a ogni merge o su tag (domanda A5) | l'immagine pubblicata si scarica e si avvia |

La 3.2 serve per il criterio del corso sugli E2E nella pipeline. Oggi `AGENTS.md` dice che si
lanciano a mano e che la Action non li esegue: il task deve cambiare quella regola.

## Fase 4: pagina viva

**Si inizia quando è disponibile il container della pipeline, anche solo con l'LLM finto.**

Prima di iniziare:

- la forma dell'API e degli eventi SSE è concordata con chi realizza la pipeline (domanda A6, in
  `docs/pipeline.md`). Conviene farlo presto, mentre le fasi precedenti sono in corso;
- per l'anteprima e i download la pipeline deve restituire un PDF e un `.tex`. Con il solo LLM finto,
  per un PDF vero serve comunque il compilatore.

| Task | Branch e titolo della PR | Contenuto | Finito quando |
|---|---|---|---|
| 4.1 Compose | `chore/repo-compose-web-pipeline`<br>`chore(repo): run web and pipeline with compose` | file Docker Compose con `web` e `pipeline`, LLM finto acceso; da concordare con chi realizza la pipeline | i due container partono con un comando |
| 4.2 Inoltro | `feat/web-api-proxy`<br>`feat(web): proxy api requests to the pipeline` | nginx inoltra `/api/*`, con il buffering spento per gli eventi SSE | dal browser `/api/status` risponde |
| 4.3 Stato | `feat/web-model-status`<br>`feat(web): show model status` | indicatore «modello occupato», blocco dell'invio, badge «test mode» | la pagina rispecchia `/api/status` |
| 4.4 Backend | `feat/web-backend-selector`<br>`feat(web): enable backend selector` | scelta tra API e locale in base ai backend disponibili | il selettore mostra i backend dichiarati dalla pipeline |
| 4.5 Invio | `feat/web-submit-text`<br>`feat(web): submit text to the pipeline` | creazione del job con testo e backend, messaggio nello storico, gestione del `409` | l'invio crea un job; se il modello è occupato si vede l'avviso |
| 4.6 Avanzamento | `feat/web-job-progress`<br>`feat(web): show job progress` | eventi SSE: in coda, blocco in corso, compilazione, finito | lo stato si aggiorna senza ricaricare la pagina |
| 4.7 Esiti | `feat/web-job-outcome`<br>`feat(web): show job outcome` | riuscito, riuscito con avvisi, fallito con la sua causa | ogni esito ha il suo messaggio, provato nei test |
| 4.8 Anteprima | `feat/web-pdf-preview`<br>`feat(web): show pdf preview` | anteprima del PDF del job concluso | il PDF si vede nella pagina |
| 4.9 Download PDF | `feat/web-pdf-download`<br>`feat(web): add pdf download` | pulsante per scaricare il PDF | il file scaricato si apre |
| 4.10 Sorgente | `feat/web-tex-source`<br>`feat(web): show and download tex source` | vista e download del `.tex` | testo mostrato e file scaricato coincidono con quelli della pipeline |
| 4.11 Annulla | `feat/web-cancel-job`<br>`feat(web): cancel the running job` | annullamento del job in corso | il job si ferma e la pagina permette un nuovo invio |
| 4.12 Rigenera | `feat/web-regenerate`<br>`feat(web): regenerate last request` | nuovo job con lo stesso testo | «rigenera» crea un job con l'ultimo testo inviato |

L'ordine è quello della tabella. Dalla 4.3 in poi ogni task aggiunge i suoi unit test, con la
pipeline simulata, e il suo end-to-end, con il container della pipeline e l'LLM finto.

## Da chiarire

- **Approvazione del professore:** l'architettura risulta ancora una bozza da far approvare;
  `docs/web.md` è stato scritto senza aspettare.
- **Test del frontend:** i criteri del corso parlano di unit test con pytest: va confermato che per
  `web` vada bene Vitest.
- **Dipendenze:** vanno approvate prima del task che le aggiunge (1.4, 3.1).
- **Mockup:** può cambiare la divisione dei task della fase 2.
