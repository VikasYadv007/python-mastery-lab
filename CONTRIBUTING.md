# Contributing

Use Python 3.11+ and run commands from the repository root. Install
`requirements-dev.txt`, then run Ruff and pytest as shown in the README.
This app runs from source; `requirements.txt` defines runtime dependencies.

## Code organization

- Put reusable validation, presentation, schema, and transfer logic in `mastery_lab/`.
- Keep `app.py` focused on Streamlit workflows and `ui_style.py` on visual styling.
- Keep `quiz_core.py` compatible with the browser, terminal, and owner tools.
- Put current guides in `docs/`; historical instructions go in `docs/archive/`.
- Add regression tests for data handling, authentication, and changed behavior.

## Data compatibility

Never change existing question IDs or replace a learner's database during upgrades.
Schema updates must be additive. Migrations and restores insert missing rows in a
transaction and preserve existing records on conflict.

Keep secrets, databases, and personal backups untracked. Tests must use temporary
storage. Reference-example tests execute only trusted, version-controlled lecture
examples; never execute imported question-pack code in the app.

## Before a pull request

Run `python -m ruff check .`, `python -m ruff format --check .`, and
`python -m pytest -q`. Describe the changed behavior, checks performed, and cloud
validation still needed. Keep unrelated changes out of the commit.
