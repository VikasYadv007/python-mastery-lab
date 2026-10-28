# Python Mastery Lab

A Python study workspace with 201 multiple-choice questions, 28 coding challenges,
saved quizzes, notes, bookmarks, and spaced revision. Use local SQLite profiles or
password-protected accounts backed by PostgreSQL.

## Quick start

Use Python **3.11 or newer**. Run from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

On macOS/Linux, activate with `source .venv/bin/activate`.
Open [localhost:8501](http://localhost:8501). Stop the server with `Ctrl+C`.
For the standard-library-only terminal quiz, run `python terminal_quiz.py`.
Terminal mode supports local profiles; unset `DATABASE_URL` before using it.

The Python Glass interface uses frosted panels, Python blue and gold accents, and
matching light/dark appearances. The top-right account selector has the appearance
switch immediately to its left.

## Study workflow

- **Overview:** explore a draggable particle sculpture with Orbit,
  Double Helix, and Wings formations, clickable progress signals, motion controls,
  a topic launchpad, quick practice, and saved-session resume.
- **Quiz Arena:** filter by lecture, topic, difficulty, and revision mode.
- **Coding:** save drafts, download Python files, inspect hints, and self-grade.
- **Review:** search and prioritize revision queues, retry questions, inspect mistake
  timelines, and plan the next seven days of revision.
- **Progress:** explore interactive charts, filter your history, set a daily target,
  start topic practice, resume saved sessions, and download backups.
- **Lectures:** import validated JSON question packs.

Run coding solutions in your own editor. The app does not execute pasted code.
Notes and drafts save when you leave their text field; explicit Save buttons are
also available. Saved dates display in IST; database timestamps use UTC.

## Configuration and progress

Without `DATABASE_URL`, progress is stored in `data/progress.sqlite3`. Preserve
this file across upgrades. Local database backups contain **all local profiles**.
Cloud ZIP backups contain the signed-in learner's history and uploaded packs.

For PostgreSQL, copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`
locally, or configure secrets in your deployment settings. Follow the
[cloud setup and migration guide](docs/cloud-setup.md). Keep credentials,
databases, and personal backups out of Git. Hosted deployments need PostgreSQL for
persistent progress.

## Repository structure

```text
app.py                  Streamlit entry point and page workflows
quiz_core.py            Persistence and quiz engine; stable public API
cloud_storage.py        PostgreSQL pool and SQL adapter
ui_style.py             Light/dark tokens, CSS, and SVG icons
mastery_lab/
  validation.py         Question-pack schema checks
  security.py           Username normalization and password hashing
  schema.py             Shared SQLite/PostgreSQL table definitions
  transfer.py           Insert-only migration and recovery logic
  presentation.py       IST formatting and safe SQLite backups
  analytics.py          Filtered metrics, streaks, and revision queues
  charts.py             Interactive Python Glass chart specifications
  overview.py           Overview data and local observatory rendering
  assets/               Authored particle scene HTML, CSS, and JavaScript
terminal_quiz.py        Offline command-line quiz
manage_users.py         Owner account creation and password recovery
migrate_progress.py     SQLite-to-PostgreSQL transfer
restore_backup.py       Per-user cloud ZIP recovery
packs/                  Versioned JSON question banks
data/                   Local progress (ignored by Git)
reference/              Source lecture PDF
tests/                  Unit, regression, and Streamlit interaction tests
docs/                   Current guides and archived UI upgrade instructions
.github/workflows/      Automated quality checks
```

## Development

```powershell
python -m pip install -r requirements-dev.txt
python -m ruff check .
python -m ruff format --check .
python -m pytest -q
```

Apply formatting with `python -m ruff format .`. GitHub Actions runs these checks
on Windows and Linux with Python 3.11 and 3.14. Tests use temporary databases and
disable the environment's cloud database configuration.

With Node.js LTS installed, run `node --test tests/overview_scene.test.cjs` for
animation controls, reduced motion, visibility pausing, and cleanup checks.
Node is needed only for these development tests; the app uses Python on the server
and the browser's built-in canvas. No graphics service or external script is used.

See [contributing](CONTRIBUTING.md), [architecture](docs/architecture.md),
[user guide](docs/user-guide.md), [topic coverage](docs/topic-coverage.md), and the
[maintenance review](docs/maintenance-review.md). For source upgrades, update the
whole source tree, including `mastery_lab/`, and reinstall requirements. Keep your
progress database and secrets; the old UI-only ZIP instructions are historical.

See [Progress and revision](docs/analytics-and-review.md) for chart interactions,
metric definitions, queue behavior, and export scopes.
See [the Overview observatory](docs/overview-observatory.md) for motion controls,
keyboard interaction, and the topic launchpad.
