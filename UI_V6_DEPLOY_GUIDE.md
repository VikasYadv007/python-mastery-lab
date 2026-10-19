# Python Mastery Lab v6 — interface overhaul and deployment

This upgrade changes only Streamlit presentation and quiz-page layout. Your existing `cloud_storage.py`, `quiz_core.py`, JSON question packs, Supabase tables, usernames, and saved progress remain unchanged.

## What changes

- Primary blue buttons have **white text explicitly applied to Streamlit's nested labels**, including form/submit labels, and satisfy WCAG AA text contrast in the light and dark palettes.
- Primary actions are **compact on desktop** instead of taking the full content width. Sidebar navigation deliberately fills the sidebar; on phones, buttons can fill their narrow column for easy tapping.
- Content width is capped at 1110px; questions and answer forms are capped around 880px for legibility.
- Light/dark surfaces, focus outlines, active navigation, answer choices, feedback panels, code areas and metrics use consistent design tokens.
- Small screens gain more predictable padding, a compact toolbar layout and two-column metric cards where supported.
- IST display formatting, account sign-in, migrations, cloud saving, bookmarks, answers and review schedules are untouched.

## Install locally first (Windows PowerShell)

1. In VS Code, open your existing `python_mastery_lab` folder and **stop Streamlit** with Ctrl+C.
2. Optional file backup (recommended):

   ```powershell
   Copy-Item app.py app.before-v6.py
   Copy-Item ui_style.py ui_style.before-v6.py
   ```

   Store backups outside the Git repository or delete them before committing so you don't upload redundant app code.
3. Unzip `Python_Mastery_Lab_UI_Overhaul_v6.zip`, then copy these files to the *same relative paths* in your existing project:

   - `app.py` (replace)
   - `ui_style.py` (replace)
   - `.streamlit/config.toml` (replace)

   You can keep `UI_V6_DEPLOY_GUIDE.md` for instructions.
4. **Do not replace or delete** `cloud_storage.py`, `quiz_core.py`, `data/progress.sqlite3`, `packs/`, `.streamlit/secrets.toml`, or your Supabase database. You also do not need to regenerate `DATABASE_URL` or `REGISTRATION_CODE` in Streamlit Cloud.
5. Check syntax and launch:

   ```powershell
   python -m py_compile app.py ui_style.py
   python -m streamlit run app.py
   ```

6. In your browser, verify Overview, Quiz arena (before and after answering), Coding dojo, Review lab, My progress, Lecture library, sign-in and sign-out; switch light/dark and shrink the browser to mobile width. Real Streamlit UI can vary by the installed Streamlit version.

## Deploy to the SAME Streamlit website

After local verification:

```powershell
git status
# stage only the UI files
git add app.py ui_style.py .streamlit/config.toml
git diff --cached --name-only
git commit -m "Improve Python Mastery Lab UI and responsive controls v6"
git fetch origin
git merge --no-edit origin/main
git push -u origin main
```

- If Git says **nothing to commit**, confirm the files were actually copied into the existing project.
- If Git reports merge conflicts, **stop and resolve them**; do not force-push and do not delete the repository.
- If you are in a pending merge, run `git status` and complete that merge first rather than starting another.
- Your Streamlit Community Cloud deployment following GitHub's `main` branch should update automatically. Check its dashboard / logs if deployment fails.
- Wait until the new version is shown, then hard-refresh the site (`Ctrl+Shift+R` on Windows) or open an incognito/private tab.
- The existing Streamlit Cloud **Secrets** remain intact; no database migration is required.
- Verify an existing unfinished quiz still opens and progress saves across a refresh.

## If colors still look wrong on deployment

Check your Streamlit deployment's latest commit and package version. Make sure `app.py` AND `ui_style.py` are both the new versions; mixing v5/v6 interface files can cause inconsistent styling. Open a private browsing session to rule out cached assets. If a particular widget still looks wrong, capture that widget plus the browser width and the Streamlit version so its specific selector can be adjusted.

## Verification performed before packaging

- 16 local automated Python tests passed, including existing quiz, cloud-storage, saved-session and UI-path checks.
- Browser **static style simulations** at 1440px and 390px, in light and dark modes: no document-level horizontal overflow; computed primary-button label text was white on blue; desktop button width was about 155px for a representative CTA.
- White-on-primary-blue contrast was 6.04:1 (light) and 6.22:1 (dark) for the theme tokens, both above the 4.5:1 WCAG AA normal-text threshold.
- Static simulations aren't a substitute for testing a real Streamlit runtime. Streamlit wasn't installable in the build environment, so the deployed rendering needs your visual confirmation.

This v6 interface uses coding-platform UX patterns like compact action areas, scannable problem cards and focused navigation. It is an original visual design, not a copy of LeetCode or Coding Ninjas assets.
