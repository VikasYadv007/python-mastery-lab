# Maintenance review — 27 October 2026

Reviewed local commit `3edd136`, which matched remote HEAD at the start of review.
Earlier uncommitted documentation and UI test changes were retained.

## Changes

- Extracted validation, security, schema, transfer, and presentation services.
- Consolidated schema definitions and migration/recovery insertion rules.
- Rejected malformed coding fields before the UI accesses them.
- Validated bundled and cloud pack bodies before indexing their IDs.
- Prevented local pack-file overwrite and invalid or duplicate quiz selection.
- Tightened password input bounds and hash decoding.
- Closed migration connections explicitly, including paths containing URL characters.
- Prevented transfers from linking learners to another learner's session.
- Abort recovery when a backup conflicts with installed lecture content or question IDs; roll back imported progress in the same transaction.
- Restricted terminal profile selection to offline storage.
- Updated runtime minimums to installed/tested releases; added explicit timezone
  data and separate development requirements.
- Applied Ruff formatting/import ordering across Python files.
- Added repository settings, contributor guidance, and a platform/version CI matrix.
- Simplified dev-container setup and removed protection-disabling launch flags.
- Moved current guides into `docs/` and old UI instructions into its archive.

## Limits

The task's final result records local checks. Production PostgreSQL connectivity,
hosted deployment, and GitHub Actions execution require their corresponding services.
No production database migration was performed. The invite-only account system still
lacks MFA, account lockout, and email recovery; those need an authentication design
change rather than formatting or repository organization.

## Local validation

- `python -m pytest -q`: **30 passed** on Windows / Python 3.14.
- Ruff lint: passed.
- Ruff format check: all Python files formatted consistently.
- Git whitespace validation: passed.

The configured GitHub CI matrix has not yet run. Changes are prepared in the local
checkout and have not been committed or pushed by this review.
