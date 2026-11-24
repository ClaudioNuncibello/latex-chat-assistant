# latex-chat-assistant

Una pagina web in forma di chat che trasforma un testo scritto in italiano naturale in un documento
PDF LaTeX. Le formule si dettano a parole, per esempio «integrale da zero a infinito di e alla meno
x quadro dx»: chi scrive deve conoscere l'italiano, non LaTeX.

## Come funziona

```
browser → web → pipeline Python → LLM + compilatore LaTeX → PDF → pipeline → web → anteprima
```

L'utente scrive il testo nella chat e, accanto, governa il modello con i controlli della pagina. Il
PDF compilato torna alla pipeline, che lo passa alla pagina: l'utente lo vede in anteprima, lo
scarica, e può vedere e scaricare anche il sorgente `.tex`. Ogni componente gira in un container
Docker:

| Componente | Cosa fa |
|---|---|
| web | serve la pagina chat e fa da adattatore tra il browser e la pipeline |
| pipeline | segmenta il testo, chiede la conversione all'LLM, valida il risultato, assembla il documento |
| LLM | modello linguistico (API di un gestore oppure Ollama in locale), scelto dalla pagina |
| compilatore | compila il LaTeX in un ambiente isolato e restituisce il PDF alla pipeline |

Il LaTeX prodotto da un LLM è trattato come non attendibile: il preambolo è un template fisso e la
compilazione avviene solo in sandbox.

## La pagina

- **Chat**: casella per il testo da inviare e storico dei messaggi della sessione.
- **Controlli del modello**, in un pannello accanto alla chat:
  - selettore del backend: API di un gestore oppure Ollama in locale;
  - indicatore «modello occupato»: mostra se il modello sta già elaborando una richiesta e blocca
    l'invio finché non è libero;
  - annulla la richiesta in corso e rigenera l'ultima.
- **Documento**: anteprima del PDF compilato, download del PDF e visualizzazione e download del
  sorgente `.tex`.

La pagina è pensata per l'uso locale, un utente alla volta, senza login.

## Stato

Il progetto è all'inizio. Per ora la repo contiene le regole di lavoro; la specifica delle
componenti e il codice arrivano con le pull request successive.

## Come si lavora

Le regole (un branch per ogni task, una pull request per ogni branch con revisione del collega,
unit test sulla pull request, convenzioni per i nomi) sono in [AGENTS.md](AGENTS.md). Lo stesso file
guida gli agenti di programmazione usati nel progetto, Claude Code e Antigravity.
