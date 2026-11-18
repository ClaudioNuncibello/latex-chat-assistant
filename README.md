# telegram-latex-assistant

Un bot Telegram che trasforma un testo scritto in italiano naturale in un documento PDF LaTeX.
Le formule si dettano a parole, per esempio «integrale da zero a infinito di e alla meno x quadro
dx»: chi scrive deve conoscere l'italiano, non LaTeX.

## Come funziona

```
utente su Telegram → bot → pipeline Python → LLM + compilatore LaTeX → PDF nella stessa chat
```

L'utente manda un messaggio di testo al bot e riceve nella chat il documento PDF. Ogni componente
gira in un container Docker:

| Componente | Cosa fa |
|---|---|
| bot | adattatore tra Telegram e la pipeline; controlla chi può usarlo |
| pipeline | segmenta il testo, chiede la conversione all'LLM, valida il risultato, assembla il documento |
| LLM | modello linguistico (API di un gestore oppure Ollama in locale), scelto da configurazione |
| compilatore | compila il LaTeX in un ambiente isolato |

Il LaTeX prodotto da un LLM è trattato come non attendibile: il preambolo è un template fisso e la
compilazione avviene solo in sandbox.

## Stato

Il progetto è all'inizio. Per ora la repo contiene le regole di lavoro; la specifica delle
componenti e il codice arrivano con le pull request successive.

## Come si lavora

Le regole (un branch per ogni task, una pull request per ogni branch con revisione del collega,
unit test sulla pull request, convenzioni per i nomi) sono in [AGENTS.md](AGENTS.md). Lo stesso file
guida gli agenti di programmazione usati nel progetto, Claude Code e Antigravity.
