# Architecture

The app runs from the repository root. `app.py` and `terminal_quiz.py` call the
stable functions in `quiz_core.py`; owner scripts use the same engine. Shared
helpers in `mastery_lab/` avoid Streamlit and database side effects at import time.

## Storage

`quiz_core.db()` selects SQLite for local paths and PostgreSQL for the default
database when cloud configuration exists. It commits successful work, rolls back
failures, and closes SQLite connections. `cloud_storage.py` manages a bounded
connection pool and adapts parameter placeholders for psycopg.

`mastery_lab/schema.py` holds additive, idempotent definitions for both backends.
Only the generated attempt-ID column differs. Both databases record the schema
version. Existing records and question IDs remain compatible.

## Question banks

Bundled JSON and hosted uploaded packs use schema version 1. Validation checks
every UI-required field, including coding titles, rubrics, and example inputs and
outputs. Loading adds display metadata and rejects duplicate pack/question IDs.
Question selection deduplicates its input.

## Accounts and transfer

Passwords use scrypt with unique salts. Malformed hashes and oversized password
inputs fail verification. Database account operations remain in the engine.
Cloud authentication is separate from local, freely named learner profiles. The
terminal refuses cloud configuration to avoid treating a profile as a login.

Migration and recovery share `mastery_lab.transfer.insert_progress()`. The caller
owns the transaction. Existing rows win conflicts; sessions belonging to another
learner abort the transfer. Local backups use SQLite's online backup API and close
handles before Windows temporary-file cleanup.

## Verification

Tests use temporary storage and disable environment cloud configuration. Real
Streamlit reruns cover interaction behavior. CI adds Windows/Linux and Python
3.11/3.14 coverage. Local success does not confirm production PostgreSQL connectivity
or successful execution of the remote workflow.
