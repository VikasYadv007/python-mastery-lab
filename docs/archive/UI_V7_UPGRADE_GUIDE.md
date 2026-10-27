# Python Mastery Lab v7 — top navigation upgrade

This package updates the existing Python Mastery Lab v6/v5 cloud app **without changing the quiz engine, Supabase tables, passwords, saved sessions, or question pack IDs**.

## What's changed

- **No left sidebar:** Overview, Quiz Arena, Coding, Review, Progress and Lectures are permanently accessible at the top.
- **Theme button:** Compact, circular, SVG-backed light/dark button in the top-right corner (also present on the login screen).
- **Responsive navigation:** Single row on desktop; a clear 3 × 2 tab grid on phones.
- **Compact actions:** Instant Practice, Coding Dojo, session completion, grading, quiz navigation and exports use tightly grouped buttons rather than distributing actions across huge columns.
- **Content density:** Reduced card padding, tighter title/description spacing, smaller hero and more consistent text sizes.
- **Existing storage:** All database, login, lecture pack, IST timestamp and backup behavior is preserved.

## Back up before installing

If you use offline SQLite, **do not delete** `data/progress.sqlite3`. If you use Supabase, your hosted records live separately, but keeping your own exported progress ZIP is still recommended.

In VS Code's PowerShell terminal, from the existing `python_mastery_lab` folder:

```powershell
Copy-Item app.py app_before_v7.py
Copy-Item ui_style.py ui_style_before_v7.py
```

> Put the backup files outside the Git repository or remove them before `git add .`; the commands below only stage the two intended files.

## Update the project

Extract the update ZIP and copy these **two files** into the root of your existing project, replacing the originals:

- `app.py`
- `ui_style.py`

Do **not** replace or remove:

- `cloud_storage.py`, `quiz_core.py`, `migrate_progress.py`
- `.streamlit/secrets.toml` or your Streamlit Community Cloud Secrets
- `data/`, `packs/` or your downloaded progress backups

No new Python dependency is required; `requirements.txt` stays unchanged.

## Test locally

```powershell
python -m py_compile app.py ui_style.py
python -m streamlit run app.py
```

Open the displayed localhost URL. Verify:

1. All six navigation items appear **at the top**, not in a sidebar.
2. Clicking Quiz Arena/Coding/Review returns the right page.
3. The round top-right button toggles both themes, including on the sign-in page.
4. The two Instant Practice buttons sit close together on desktop.
5. Quiz questions, explanations, bookmarks and session saving work as before.
6. If using cloud mode, your account and existing Supabase history still appear.

At phone widths, navigation displays as two rows of three compact tabs.

## Push to GitHub and redeploy Streamlit

Stop your local app with `Ctrl+C` and use **exactly these files** for the UI update:

```powershell
git status
git add app.py ui_style.py
git diff --cached --name-only
git commit -m "Move Python Mastery Lab navigation to top v7"
git fetch origin
git merge --no-edit origin/main
git push -u origin main
```

If `git merge` shows conflicts, stop and resolve them; **don't force-push**. Streamlit Community Cloud normally picks up a successful push to the connected `main` branch automatically. Open your existing app and hard-refresh with `Ctrl+Shift+R`.

**Do not create a new Supabase database or a second Streamlit deployment.** Existing Streamlit Secrets (`DATABASE_URL`, `REGISTRATION_CODE`) are untouched.

## Verification notes

The package passed the local backend/UI-path tests, and a static Chromium style preview was checked at desktop and phone sizes in both modes. A true live Streamlit-rendered screenshot was **not** available in this environment; browser and Streamlit version differences may affect final visual details.
