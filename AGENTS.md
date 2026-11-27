# latex-chat-assistant

Pagina web in forma di chat che converte italiano naturale (formule dettate a parole comprese) in un
PDF LaTeX, con anteprima e download del PDF e del sorgente. Componenti, ognuna in un container
Docker: web → pipeline Python → LLM e compilatore.

Specifica: `docs/architettura-generale.md` (requisiti e quadro d'insieme) e un file per ogni
componente, `docs/<componente>.md` (`web`, `pipeline`, `llm`, `compiler`). Prima di lavorare su una
componente, leggere il suo file. Le regole di lavoro stanno solo in questo file.

Se esiste `docs/handoff.md`, leggerlo per primo: dice dove si era rimasti e cosa fare.

Issue tracker: GitHub, con `gh`. Come si pubblicano e si leggono i ticket: `docs/agents/issue-tracker.md`.

## Lingua

Prosa e documentazione in italiano. Identificatori, nomi di file, commenti nel codice, branch,
commit e titoli di PR in inglese.

## Spiegare il lavoro

Regola importante: chi segue il lavoro deve capire tutto quello che si fa, mentre si fa. L'agente
spiega in chat, in italiano semplice, definendo i termini tecnici la prima volta che li usa.

- **Prima di un task:** cosa si farà, a cosa serve nel progetto e quali file si toccano.
- **Durante:** per ogni passo, cosa fa e perché si fa così. Vale anche per file di configurazione,
  dipendenze e comandi.
- **A task finito:** cosa è cambiato file per file, come provarlo, con quale esito è stato provato e
  cosa resta da fare.
- **A fase finita** (le fasi di un piano, per esempio `docs/web-piano.md`): cosa funziona adesso,
  come si collegano le parti realizzate e quale fase viene dopo.

## Un branch, un task, una PR

- Ogni task ha un branch dedicato, creato da `main` aggiornato. Il task è il più piccolo possibile:
  una sola cosa che si descrive in una riga.
- A implementazione finita si pubblica il branch con `git push` e ci si ferma: la PR la scrive e
  la apre l'utente a mano su GitHub, dove il template è già nella descrizione. L'agente apre la
  PR (`gh pr create`) solo se l'utente lo chiede, e in quel caso segue lo stesso template.
- Il merge spetta al collega dopo la revisione. Su `main` si arriva solo con una PR (push diretti,
  force push e cancellazione sono bloccati dalla protezione del branch).
- La descrizione della PR segue `.github/pull_request_template.md`: cosa cambia, come è stato
  testato (unit, e2e eseguiti o no, con esito), a quale task si riferisce.
- Merge in squash: su `main` resta un commit per PR. Il branch non si cancella dopo il merge:
  resta come storico del lavoro, con i suoi commit.

## Nomi di branch, commit e PR

Tipo = `feat`, `fix`, `refactor`, `test`, `docs`, `chore` (configurazione, dipendenze).
Tutto minuscolo, con i trattini.

| Cosa | Forma | Esempio |
|---|---|---|
| Branch | `<tipo>/<componente>-<descrizione-breve>` | `feat/web-model-selector` |
| Titolo PR e commit | `<tipo>(<componente>): <verbo all'imperativo> ...` | `fix(pipeline): reject empty text` |

## Test

- Ogni script ha i suoi unit test, scritti nello stesso task.
- Gli unit test girano come GitHub Action sulla PR; se falliscono, il merge è impedito.
  La coverage deve restare almeno al 90% (`fail_under` in `pyproject.toml`): sotto, la Action fallisce.
- Sulla PR gira anche la Action di lint (`ruff check`, `ruff format --check`, `ty check`). Prima
  di pubblicare il branch si lanciano gli stessi comandi in locale (sezione Comandi).
- Per ora la Action non esegue gli end-to-end né la build Docker.
- Gli end-to-end partono a mano, quando una modifica tocca i punti che coprono. Eseguirli e
  riportare l'esito nella PR.

## Struttura della repo

Una cartella per componente. I test stanno fuori dalle componenti, con una sottocartella per
componente e un `test_<file>.py` per ogni file testato:

```
<componente>/
  <file>.py
tests/
  unit/<componente>/test_<file>.py
  e2e/<componente>/
  e2e/system/                       # percorsi che attraversano più componenti
```

Fuori dalle componenti: `scripts/` (strumenti del repo, con i loro test in `tests/unit/scripts/`),
`agent-skills/` (sorgenti delle skill) e `docs/`.

## Skill degli agenti

Le skill condivise sono `to-tickets`, `implement`, `tdd`, `code-review` e `handoff`. Claude Code le
legge da `.claude/skills/`, Antigravity da `.agents/skills/`.

- L'unica fonte è `agent-skills/`. Si modifica lì, poi si lancia
  `uv run python scripts/sync_agent_skills.py`, che copia le skill nelle due cartelle degli agenti.
  Le copie in `.claude/skills/` e `.agents/skills/` si committano insieme ai sorgenti e non si
  modificano a mano.
- `uv run python scripts/sync_agent_skills.py --check` esce con errore se una copia è diversa dalla
  fonte.
- `handoff` scrive `docs/handoff.md`, che si committa e si pusha con una PR come ogni altro file.

## Dipendenze (uv)

- Solo forma ufficiale di uv: `pyproject.toml` e `uv.lock`. Un `requirements.txt` non esiste.
- Workspace: `pyproject.toml` nella radice, più un `pyproject.toml` per ogni componente con le sue
  dipendenze. Il `uv.lock` è uno solo, nella radice, e si modifica solo con uv.
- `[dependency-groups].dev` (es. `pytest`) sta nel `pyproject.toml` della radice, perché i test
  sono fuori dalle componenti.
- Ogni immagine Docker installa solo la sua componente: `uv sync --package <componente>`.
- Una dipendenza nuova si chiede all'utente prima di aggiungerla.

## Comandi

```
uv sync          # installa il workspace
uv run pytest                      # unit test con coverage (soglia 90%)
uv run ruff check .                # lint
uv run ruff format .               # formattazione (--check per solo verificare)
uv run ty check                    # type check
uv run python scripts/sync_agent_skills.py            # copia agent-skills/ per i due agenti
uv run python scripts/sync_agent_skills.py --check    # verifica che le copie siano allineate
```

> Aggiornare questa sezione quando si aggiunge un comando.
