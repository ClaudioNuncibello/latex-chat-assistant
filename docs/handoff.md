# Handoff

Stato al 2026-11-19. Serve a chi riparte da zero (persona o agente) nella repo ufficiale.
Le regole di lavoro sono in `AGENTS.md`: leggerle prima di toccare qualcosa.

## Dove siamo

Si sta preparando la repo: ambiente, CI, protezione di `main` e skill degli agenti. Codice
applicativo ancora zero. Il lavoro di specifica è stato scritto nella repo di prova e va importato
qui con PR.

**Repo ufficiale** (`telegram-latex-assistant`, pubblica). Collaboratori: l'autore e `Andrea-P18`
(scrittura). `main` contiene: primo commit, `CODEOWNERS` (push diretto, unica eccezione), PR #1
(workspace uv, template PR, merge commit), #2 (i branch non si cancellano), #3 (Action unit test su
Ubuntu, Windows, macOS), #4 (script `scripts/sync_agent_skills.py` con i suoi 11 unit test).

**Protezione di `main`** (ruleset `main`, attivo, solo sul branch di default): PR obbligatoria con 1
approvazione, solo squash, i tre controlli `unit-tests (...)` verdi, niente cancellazione. Bypass:
solo l'admin e solo sulle PR (per emergenze). Il force push non è bloccato esplicitamente.

**Branch pronto, non ancora pubblicato:** `feat/agent-skills-add-shared-skills`, sopra `main`
aggiornato (rebase fatto). Quattro commit, l'ultimo è questo handoff (stesso branch, scelta
dell'utente: due PR per soli file md non servivano). Gli altri tre:
`feat(agent-skills): add shared skills` (le cinque skill in `agent-skills/`),
`feat(agent-skills): sync skill copies for the agents` (le copie in `.claude/skills/` e
`.agents/skills/`, generate dallo script) e `chore(ci): check agent skills are in sync` (nuovo passo
`--check` nell'Action). In locale: 11 unit test passano, `--check` esce con 0 e fallisce se una
copia viene modificata a mano. Da pubblicare con
`git push -u origin feat/agent-skills-add-shared-skills`; la PR la scrive e la apre l'utente.

**Remoto sporco di storia:** `origin/docs/repo-handoff` contiene un vecchio handoff e le skill con
il vecchio titolo. Non si cancella (i branch restano come storico) e non serve a niente: il lavoro
vero è in `feat/agent-skills-add-shared-skills`.

**Repo di prova** (`latex-assistant`, privata, in locale in `~/Documents/GitHub/latex-assistant`):
la bozza della specifica sta in `ProgettoFinale/`, branch `docs/final-project-claude-md`, **mai
pushata**. Contiene `architettura-generale.md`, `docs/bot.md` e `docs/agents/issue-tracker.md`. Le
skill sono già passate in questa repo. I commit di quel branch hanno un trailer
`Co-Authored-By: Claude`: non importarli, copiare solo i file.

## Prossimi passi, in ordine

1. Pubblicare `feat/agent-skills-add-shared-skills`, aprire la PR e farla approvare da Andrea (tre
   controlli verdi, squash). Le skill sono già attive solo dopo il merge.
2. PR `docs`: portare in `docs/` `architettura-generale.md`, `bot.md` e `agents/issue-tracker.md`
   dalla repo di prova (la prima va in `docs/`, non nella radice).
3. Creare l'etichetta `ready-for-agent` (`gh label create ready-for-agent`) e i ticket iniziali:
   specifica di pipeline, LLM e compilatore (`docs/pipeline.md`, `docs/llm.md`,
   `docs/compiler.md`) e scheletro del bot.
4. Chiudere le domande aperte di `docs/bot.md` (sezione 7): libreria Telegram, Telegram finto per
   gli e2e, reti Docker, utente non autorizzato negli e2e, intervallo di polling. Le dipendenze
   nuove (libreria Telegram, `telethon`) si chiedono prima all'utente.

## Accordi presi, non scritti altrove

- La PR la scrive e la apre l'utente a mano. L'agente fa `git push` e si ferma; apre la PR solo se
  glielo chiedono.
- Niente `Co-Authored-By` né «Generated with Claude Code» in commit e PR.
- Un branch, un task, una PR, ma per i soli file di documentazione (handoff compreso) l'utente
  accetta che viaggino nella PR del task a cui si riferiscono, senza una PR a parte.
- Il periodo di auto-review è finito con la #3: da #4 ogni PR la rivede l'altro collaboratore.
- Niente `.gitattributes` né `.editorconfig` (scelta dell'utente).
- Gli end-to-end partono a mano e non stanno nelle Action. Schema scelto: client utente Telethon
  contro il bot vero, pipeline finta (dettagli in `docs/bot.md`).

## Cose da sapere

- Il check macOS può restare in coda a lungo (dopo 15 minuti è stato annullato per mancanza di runner, il
  2026-11-18, senza che pytest partisse). Non è un test fallito: si rilancia con
  `gh run rerun <id> --failed`. È comunque obbligatorio per il merge. Se capita spesso, le strade
  sono un runner macOS diverso o togliere macOS dai controlli obbligatori: decide l'utente.
- Senza `.python-version` uv sceglie Python 3.14: nella repo è fissato a 3.12.
- Se in un terminale è impostata `VIRTUAL_ENV` di un'altra repo, `uv` avvisa e la ignora: aprire un
  terminale nuovo nella cartella.
- `to-tickets` e `code-review` nominano `/setup-matt-pocock-skills`, che qui non esiste: basta
  `docs/agents/issue-tracker.md`, che arriva con la PR `docs` (punto 2).
- Le copie in `.claude/skills/` e `.agents/skills/` non si modificano a mano: si cambia
  `agent-skills/` e si rilancia la sync, altrimenti l'Action fallisce.

## Skill suggerite

`to-tickets` per i ticket del punto 3, `tdd` e `implement` quando si scrive codice, `code-review`
prima di chiedere la revisione, `handoff` per aggiornare questo file. Claude Code le legge da
`.claude/skills/` e Antigravity da `.agents/skills/` dopo il merge del punto 1; fino ad allora sono
in `~/.claude/skills`.
