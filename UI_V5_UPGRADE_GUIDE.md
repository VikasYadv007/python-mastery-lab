# Python Mastery Lab v5 — UI and theme upgrade

This is a **visual-only update to the v4 cloud-enabled application**. It keeps `quiz_core.py`, `cloud_storage.py`, the PostgreSQL schema, answer IDs, and all question packs unchanged.

## Update your existing folder (recommended)

1. Back up the existing `app.py`, `ui_style.py`, and `.streamlit/config.toml`, or make a Git commit before replacing them.
2. Download the **UI Update v5** ZIP, extract it, and copy these three files into the same paths in your local `python_mastery_lab` folder:
   - `app.py`
   - `ui_style.py`
   - `.streamlit/config.toml`
3. **Do not replace** `quiz_core.py`, `cloud_storage.py`, `packs/`, `data/`, or `.streamlit/secrets.toml` in your existing installation. Your `DATABASE_URL` and `REGISTRATION_CODE` stay in your existing Streamlit Cloud Secrets and optional local `.streamlit/secrets.toml`.
4. Stop the previous local Streamlit process using `Ctrl+C`, then from the project directory run:

   ```powershell
   python -m pip install -r requirements.txt
   python -m streamlit run app.py
   ```

5. Open the app locally, sign in, visit all six sections, and test both appearances. The Dark mode switch appears even on the sign-in page.
6. Check your GitHub changes (especially for secrets!):

   ```powershell
   git status
   git add app.py ui_style.py .streamlit/config.toml
   git diff --cached --name-only
   git commit -m "Refresh Mastery Lab UI: accessible light and dark themes"
   git fetch origin
   git merge --no-edit origin/main
   git push origin main
   ```

   **Do not use `git push --force`.** If Git says a merge is in progress, or reports a conflict, resolve it before running further merge/push commands. If `git merge` says `Already up to date`, continue normally.
7. Visit Streamlit Community Cloud and open the app deployed from that repository's `main` branch. Code changes normally trigger a redeployment. If necessary, reboot the app using the Streamlit app-management interface, then hard-refresh with `Ctrl+Shift+R` (on macOS `Cmd+Shift+R`). On phones, close/reopen or use a fresh tab.

## Cloud data safety

- Your progress remains in the **same Supabase PostgreSQL database** because v5 does not modify your connection code or tables.
- Do **not** delete/change the `DATABASE_URL` secret or create a new Supabase project for this UI update.
- `.streamlit/secrets.toml`, `.env`, SQLite databases, and private backups must never be committed to GitHub.
- As with any hosted database, continue downloading occasional progress backups from **My progress**.

## Visual improvements

- More contrast between the page background, individual cards, forms and selected MCQ answers.
- Separate accessible tokens for text, success, mistakes, warnings, and primary/secondary actions in both themes.
- Stronger borders and focus indicators, usable navigation icons, a persistent Menu, and a polished sign-in layout.
- Styled selectors, radios, checkboxes, tabs, expanders, inputs, text areas, tables, uploads, code blocks, and progress summaries.
- Mobile CSS (including 390px viewport checks), horizontal scrolling of wide tables, and reduced-motion preference support.
- Clear cloud storage labels; time in IST continues unchanged.

## Validation and limitations

- The original backend/smoke suite plus new color-contrast regressions passed (`14 passed`).
- Static Chromium mockups were reviewed at 1440px and 390px in light/dark modes; no page-level horizontal overflow was detected in those mockups.
- The visual mockups are **not** screenshots from a live Streamlit deployment. Streamlit itself was not installed in the build environment, so a final live browser review on your specific Streamlit version is still needed.
- If a Streamlit update changes internal HTML attributes, some CSS selectors may need adjustment; no CSS customization can guarantee all future versions' exact rendering.
