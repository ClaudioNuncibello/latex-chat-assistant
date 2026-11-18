# Handoff

Stato al 2026-11-18. Serve a chi riparte da zero (persona o agente) nella repo ufficiale.
Le regole di lavoro sono in `AGENTS.md`: leggerle prima di toccare qualcosa.

## Dove siamo

Si sta preparando la repo: ambiente, CI e protezione di `main`. Codice applicativo ancora zero.
Il lavoro di specifica è stato scritto nella repo di prova e va importato qui con PR.

**Repo ufficiale** (`telegram-latex-assistant`, pubblica). Collaboratori: l'autore e `Andrea-P18`
(scrittura). `main` contiene: primo commit, `CODEOWNERS` (push diretto, unica eccezione), PR #1
(workspace uv, template PR, merge commit), #2 (i branch non si cancellano), #3 (Action unit test su
Ubuntu, Windows, macOS).

**Protezione di `main`** (ruleset `main`, attivo, solo sul branch di default): PR obbligatoria con 1
approvazione, solo squash, i tre controlli `unit-tests (...)` verdi, niente cancellazione. Bypass:
solo l'admin e solo sulle PR (per emergenze). Il force push non è bloccato esplicitamente.

**PR aperta:** #4 `feat(scripts): add agent skills sync script` (branch
`feat/scripts-sync-agent-skills`), in attesa della revisione di Andrea. È la prima con un test vero
e la prima che passa dalla protezione.

**Repo di prova** (`latex-assistant`, privata, in locale in `~/Documents/GitHub/latex-assistant`):
la bozza della specifica sta in `ProgettoFinale/`, branch `docs/final-project-claude-md`, **mai
pushata**. Contiene `architettura-generale.md`, `docs/bot.md`, `docs/agents/issue-tracker.md`,
`agent-skills/` (5 skill) con le copie in `.claude/skills/` e `.agents/skills/`. I commit di quel
branch hanno un trailer `Co-Authored-By: Claude`: non importarli, copiare solo i file.

## Prossimi passi, in ordine

1. Merge di #4 (approvazione di Andrea, tre controlli verdi, squash).
2. PR `feat(agent-skills): add shared skills`: copiare `agent-skills/` da `ProgettoFinale/`, lanciare
   `uv run python scripts/sync_agent_skills.py`, aggiungere all'Action il passo
   `uv run python scripts/sync_agent_skills.py --check`.
3. PR `docs`: portare in `docs/` `architettura-generale.md`, `bot.md` e `agents/issue-tracker.md`
   dalla repo di prova (la prima va in `docs/`, non nella radice).
4. Creare l'etichetta `ready-for-agent` (`gh label create ready-for-agent`) e i ticket iniziali:
   specifica di pipeline, LLM e compilatore (`docs/pipeline.md`, `docs/llm.md`,
   `docs/compiler.md`) e scheletro del bot.
5. Chiudere le domande aperte di `docs/bot.md` (sezione 7): libreria Telegram, Telegram finto per
   gli e2e, reti Docker, utente non autorizzato negli e2e, intervallo di polling. Le dipendenze
   nuove (libreria Telegram, `telethon`) si chiedono prima all'utente.

## Accordi presi, non scritti altrove

- La PR la scrive e la apre l'utente a mano. L'agente fa `git push` e si ferma; apre la PR solo se
  glielo chiedono.
- Niente `Co-Authored-By` né «Generated with Claude Code» in commit e PR.
- Il periodo di auto-review è finito con la #3: da #4 ogni PR la rivede l'altro collaboratore.
- Niente `.gitattributes` né `.editorconfig` (scelta dell'utente).
- Gli end-to-end partono a mano e non stanno nelle Action. Schema scelto: client utente Telethon
  contro il bot vero, pipeline finta (dettagli in `docs/bot.md`).

## Cose da sapere

- Un check macOS può stare in coda anche 5 minuti: è normale, ma è obbligatorio per il merge.
- Senza `.python-version` uv sceglie Python 3.14: nella repo è fissato a 3.12.
- Se in un terminale è impostata `VIRTUAL_ENV` di un'altra repo, `uv` avvisa e la ignora: aprire un
  terminale nuovo nella cartella.
- `to-tickets` e `code-review` nominano `/setup-matt-pocock-skills`, che qui non esiste: basta
  `docs/agents/issue-tracker.md`.

## Skill suggerite

`to-tickets` per i ticket del punto 4, `tdd` e `implement` quando si scrive codice, `code-review`
prima di chiedere la revisione, `handoff` per aggiornare questo file. Le prime quattro entrano
con il punto 2; fino ad allora sono solo in `~/.claude/skills`.
