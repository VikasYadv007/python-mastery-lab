# Cloud setup and progress migration

**What is implemented:** hosted PostgreSQL (Supabase or other managed Postgres), password-protected separate accounts, automatic non-destructive table creation, persistent session/attempt/mastery/bookmark/note/draft records, persistent uploaded JSON lecture packs, full ZIP backup, SQLite-to-cloud transfer and backup restore.

**What is not done for you:** You must create a Supabase project and supply its database connection string privately. We have no access to your Supabase account. Do not put the connection string, password, invitation code, or learner SQLite data in GitHub, even in a private repo.

## 1. Create your Supabase free database

1. Open <https://supabase.com/dashboard> and create a new project (choose an appropriate region, e.g. Mumbai or nearby). Save the project database password in a password manager.
2. When it's ready, open the project's **Connect** panel. Choose **Session pooler** (port **5432**), especially on Streamlit Community Cloud/IPv4. Copy the **entire provided connection string**, including the pooler username `postgres.PROJECT_REF`, host, database, and password. Do not substitute the direct IPv6 connection string. If needed, append `?sslmode=require` (or `&sslmode=require` if URL already has `?`). URL-encode reserved symbols in your password, or use the connection URL supplied by Supabase.
3. You do **not** need to paste SQL into the Supabase editor: the app creates its own tables with `CREATE TABLE IF NOT EXISTS` when it starts. Never run `DROP TABLE` or delete the Supabase project when updating your app.
4. Generate an independent private invitation code in PowerShell:

   ```powershell
   python -c "import secrets; print(secrets.token_urlsafe(24))"
   ```

## 2. Configure Streamlit Cloud secrets

In your deployed app's **Settings → Secrets** (or during deployment in **Advanced settings → Secrets**), add exactly these two *top-level* TOML entries:

```toml
DATABASE_URL = "postgresql://postgres.YOUR_PROJECT_REF:YOUR_URL_ENCODED_PASSWORD@YOUR_REAL_POOLER_HOST:5432/postgres?sslmode=require"
REGISTRATION_CODE = "YOUR_PRIVATE_RANDOM_INVITATION_CODE"
```

These are illustrative placeholders only; **copy the real Session pooler URL** from your own Supabase project. Do not paste these values in your source code or commit them to GitHub. Restart/reboot the deployed app after changing secrets.

The app now uses the **hosted database whenever `DATABASE_URL` exists**. If it is missing, it falls back to **local SQLite only** and displays a warning; never rely on that mode for cloud persistence.

## 3. Install the new code, push to GitHub, redeploy

Back up your current progress first. Update the full source tree, including
`mastery_lab/`, owner tools, and requirements. Keep your existing `data/`, secrets,
and question IDs. Run all commands below from the repository root.

Open the project folder in the VS Code terminal:

```powershell
python -m pip install -r requirements.txt
git status --short
# If previously tracked, remove sensitive files from Git's INDEX only:
git rm --cached --ignore-unmatch data/progress.sqlite3 .streamlit/secrets.toml
git add .
git commit -m "Add permanent PostgreSQL learning history and private accounts"
git push origin main
```

`git rm --cached` does not delete the underlying local file. If the secret or SQLite file was pushed to GitHub earlier, remove its Git history and rotate exposed credentials; `.gitignore` does not erase previous commits.

Streamlit Community Cloud normally redeploys from your GitHub `main` branch. Watch **Manage app → Logs** if deployment fails. PostgreSQL packages are included in `requirements.txt`.

## 4. Create your first account

Open the deployed app. Select **Create an account** and supply:

- Unique login username (e.g. `student1`)
- A password of 10 or more characters (use a long unique passphrase)
- Your private `REGISTRATION_CODE`

Share the invitation code **only** with your 2–3 intended learners. Each creates their own username/password. The app hashes their passwords using `hashlib.scrypt`; database rows for questions and progress are filtered to the current username. Signing out or refreshing the browser requires a new sign-in, but saved progress remains.

With `REGISTRATION_CODE` omitted, self-registration is disabled; the owner can create users locally with `python manage_users.py create student1` after setting the database environment variable.

> Security model: All database connections and credentials are server-side, not exposed as browser API keys. Because this is a small invite-only app, it uses simple password accounts. It's **not** a full identity provider with password reset email, rate limiting, MFA, or OAuth. Do not use the same password elsewhere. For any public or larger-scale application, consider adopting Supabase Auth with comprehensive authorization and RLS.

## 5. Transfer all of your old local history (important!)

The old progress will not automatically appear under your new cloud username. Copy it once using the migration tool. **Do not remove the local SQLite file.**

First, find your old profile name:

```powershell
python migrate_progress.py --list-profiles
```

Then **in your OWN VS Code terminal**, set the connection string for this one PowerShell session (prompt keeps the URL out of your shell command history):

```powershell
$env:DATABASE_URL = Read-Host "Paste your private Supabase SESSION pooler database URL"
```

If you created an account named `student1`, run:

```powershell
python migrate_progress.py --from-profile "My Python practice" --to-user student1
```

Specify a different profile string exactly as shown by `--list-profiles`. The migration copies completed and unfinished sessions, every MCQ/coding attempt, spaced-review mastery, bookmarks, personal notes, and code drafts, preserving saved timestamps. Its operation is **transactional and repeatable**: rerunning it skips rows already imported and never deletes or overwrites cloud records. If the cloud account already has progress for the same question, cloud's existing conflicting row wins. For any other learner, use that learner's old profile and cloud username.

To clear the terminal environment variable afterwards:

```powershell
Remove-Item Env:DATABASE_URL
```

## 6. Use the SAME database across app updates

- For cloud redeployments, **never replace your Supabase project**, change `DATABASE_URL` to an unrelated empty database, or execute destructive SQL.
- Updating GitHub source files or adding new question packs does **not** erase the remote tables.
- Uploaded JSON lecture packs are saved in PostgreSQL too. Git-tracked `packs/*.json` stay in GitHub; keep their question IDs stable. If a previously uploaded pack is later committed into GitHub, do not simultaneously keep an incompatible duplicate `pack_id` in the DB.
- Future schema changes should be implemented as versioned, additive PostgreSQL migrations. This package creates `schema_migrations` and initializes schema version 1. **Future app updates must continue to use non-destructive migrations**; no upgrade can guarantee data safety if it contains a deliberately destructive change.
- All quiz dates continue to display in **Indian Standard Time**. The database stores original UTC timestamps.

## 7. Make backups (and how to restore)

A free hosted database is persistent across redeployments, **not an unconditional forever guarantee**. Supabase free projects may pause after a week of low activity and the free plan does not include automatic daily backups. You can resume paused projects from the Supabase dashboard, but do not depend on indefinite retention.

From each user's **My progress → Export & backup**, download **Download full progress backup (ZIP)** periodically. It includes all their session rows, attempts, mastery/review information, bookmarks, personal notes, coding drafts and shared uploaded lecture packs. Store a copy outside Streamlit/Supabase/GitHub (e.g. encrypted drive). Also back up the entire DB using `pg_dump` or Supabase CLI `db dump` periodically if you want a disaster-recovery backup of all users, passwords, and schema at once. The user ZIP intentionally excludes login password hashes.

If a project is lost, create a new Supabase project, set `DATABASE_URL`, create the user again, and run this command **locally as the owner** (with the new DB URL already set):

```powershell
python restore_backup.py python_mastery_student1_backup.zip --to-user student1
```

It inserts missing data and does not delete existing rows. Uploaded packs are restored as well. Never commit user backup ZIPs or pass them to strangers.

For a forgotten password, the owner can reset it securely from their own machine after configuring `DATABASE_URL`:

```powershell
python manage_users.py reset student1
```

## Local operation

- Without `DATABASE_URL`: original SQLite app behavior works, but **no cloud persistence**.
- With `.streamlit/secrets.toml` holding the same secrets as Streamlit Cloud: your local app connects to the **same** PostgreSQL records as the deployed app.
- The terminal-only `terminal_quiz.py` continues to use SQLite unless the `DATABASE_URL` environment variable is set before launching.

**Official references**:
- Streamlit secret configuration: <https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management>
- Supabase Postgres connection methods: <https://supabase.com/docs/guides/database/connecting-to-postgres>
- Supabase free project pausing: <https://supabase.com/docs/guides/platform/free-project-pausing>
- Supabase backup policy: <https://supabase.com/docs/guides/platform/backups>
