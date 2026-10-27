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

- **Overview:** start Smart Mix practice or continue a saved quiz.
- **Quiz Arena:** filter by lecture, topic, difficulty, and revision mode.
- **Coding:** save drafts, download Python files, inspect hints, and self-grade.
- **Review:** revisit mistakes, due questions, and bookmarks.
- **Progress:** inspect performance and download backups.
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

See [contributing](CONTRIBUTING.md), [architecture](docs/architecture.md),
[user guide](docs/user-guide.md), [topic coverage](docs/topic-coverage.md), and the
[maintenance review](docs/maintenance-review.md). For source upgrades, update the
whole source tree, including `mastery_lab/`, and reinstall requirements. Keep your
progress database and secrets; the old UI-only ZIP instructions are historical.
