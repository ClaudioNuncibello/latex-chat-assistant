# Componente `web`

Serve la pagina in forma di chat. Cosa deve fare la pagina è in `docs/architettura-generale.md`
(sezioni 1, 5.1 e 9).

## Stack

| Parte | Scelta |
|---|---|
| Pagina | React e TypeScript, costruita con Vite |
| Server | nginx, nell'immagine `nginxinc/nginx-unprivileged` (utente non privilegiato, porta 8080) |
| Pacchetti | npm |
| Unit test | Vitest con jsdom, coverage almeno al 90% |

- La logica dell'interfaccia sta nella pagina, quindi nel browser. In `web` non c'è un backend
  scritto da noi.
- nginx serve i file statici. Quando ci sarà la pipeline, inoltrerà anche `/api/*`: il browser parla
  con un solo indirizzo e la pipeline resta sulla rete Docker.

## Container

`web/Dockerfile` ha due fasi: Node installa i pacchetti e costruisce la pagina, poi l'immagine
finale riceve solo nginx e i file statici. Il contesto di build è la cartella `web/`;
`web/.dockerignore` esclude pacchetti, file generati, test e file `.env`.

La porta si pubblica solo su `127.0.0.1`, perché la pagina non ha login.

## File

`web/` è un progetto npm autonomo, con dentro i suoi test.

```
web/
  Dockerfile
  .dockerignore
  nginx.conf
  index.html
  package.json            # dipendenze e script
  package-lock.json       # versioni bloccate, lo modifica solo npm
  tsconfig.json
  vite.config.ts          # configurazione di Vite e Vitest
  src/
    main.tsx              # monta l'applicazione nella pagina
    App.tsx               # componente principale
  tests/
    unit/
      test_main.tsx
      test_App.tsx
```

I comandi sono in `AGENTS.md`.

## Stato

La pagina è bianca: `App` contiene solo un'area vuota. I passi successivi sono in
`docs/web-piano.md`.

## Aperto

- I criteri del corso parlano di unit test con pytest: va confermato che per `web` vada bene Vitest.
- Strumenti di lint e formattazione e controlli di `web` sulla PR: non ancora presenti.
