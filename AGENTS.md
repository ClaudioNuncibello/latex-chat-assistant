# telegram-latex-assistant

Bot Telegram che converte italiano naturale (formule dettate a parole comprese) in un PDF LaTeX.
Componenti, ognuna in un container Docker: bot → pipeline Python → LLM e compilatore.

Specifica: `docs/architettura-generale.md` (requisiti e quadro d'insieme) e un file per ogni
componente, `docs/<componente>.md` (`bot`, `pipeline`, `llm`, `compiler`). Prima di lavorare su una
componente, leggere il suo file. Le regole di lavoro stanno solo in questo file.

Se esiste `docs/handoff.md`, leggerlo per primo: dice dove si era rimasti e cosa fare.

Issue tracker: GitHub, con `gh`. Come si pubblicano e si leggono i ticket: `docs/agents/issue-tracker.md`.

## Lingua

Prosa e documentazione in italiano. Identificatori, nomi di file, commenti nel codice, branch,
commit e titoli di PR in inglese.

## Un branch, un task, una PR

- Ogni task ha un branch dedicato, creato da `main` aggiornato. Il task è il più piccolo possibile:
  una sola cosa che si descrive in una riga.
- A implementazione finita si apre una PR e ci si ferma: il merge spetta al collega dopo la
  revisione. Su `main` si arriva solo con una PR (push diretti, force push e cancellazione sono
  bloccati dalla protezione del branch).
- La descrizione della PR dice: cosa cambia, come è stato testato (unit, e2e eseguiti o no, con
  esito), a quale task si riferisce. Segue `.github/pull_request_template.md`, anche quando la PR
  si apre da riga di comando con `gh pr create`.
- Merge in squash: su `main` resta un commit per PR. Il branch si cancella dopo il merge.

## Nomi di branch, commit e PR

Tipo = `feat`, `fix`, `refactor`, `test`, `docs`, `chore` (configurazione, dipendenze).
Tutto minuscolo, con i trattini.

| Cosa | Forma | Esempio |
|---|---|---|
| Branch | `<tipo>/<componente>-<descrizione-breve>` | `feat/bot-start-command` |
| Titolo PR e commit | `<tipo>(<componente>): <verbo all'imperativo> ...` | `fix(pipeline): reject empty text` |

## Test

- Ogni script ha i suoi unit test, scritti nello stesso task.
- Gli unit test girano come GitHub Action sulla PR; se falliscono, il merge è impedito.
  La Action esegue solo gli unit test.
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
uv run pytest tests/unit
uv run python scripts/sync_agent_skills.py            # copia agent-skills/ per i due agenti
uv run python scripts/sync_agent_skills.py --check    # verifica che le copie siano allineate
```

> Aggiornare questa sezione quando si aggiunge un comando.
