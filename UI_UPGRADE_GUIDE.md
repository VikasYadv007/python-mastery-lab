# Python Mastery Lab — v3 UI and Accessibility Update

## Recommended: update your existing installation without resetting your study progress

1. **Stop Streamlit** in the VS Code terminal with `Ctrl+C`.
2. Back up your existing `data/progress.sqlite3` to a safe place (if present).
3. Extract `Python_Mastery_Lab_UI_Update_v3.zip`. Copy these **three** files into the SAME existing folder where `quiz_core.py` lives:
   - `app.py` — replace the old file.
   - `ui_style.py` — **new file**, add alongside `app.py`.
   - `.streamlit/config.toml` — replace the old config with the included file.
4. **DO NOT replace or delete** `data/`, `packs/`, `quiz_core.py`, or your lecture question packs. Those hold your learning progress and question IDs.
5. From the project folder in VS Code, run:

   ```bash
   python -m streamlit run app.py
   ```

6. Hard-refresh your browser once with `Ctrl+Shift+R` (`Cmd+Shift+R` on macOS).

If you are missing the underlying project files, use `Python_Mastery_Lab_Full_v3.zip` instead, then copy your old `data/progress.sqlite3` and any added `packs/*.json` into the new extracted project.

## UI fixes included

- **Font-independent navigation icons:** Sidebar controls use *embedded SVGs*, not special characters, icon fonts, external websites, or downloaded image assets. They should display consistently across Windows, macOS and browsers.
- **Sidebar recovery:** The previous CSS rule hiding Streamlit's toolbar is removed. Streamlit's built-in sidebar open/close arrow is left visible, and there is an independent **Menu** popover at the top of every page; you can navigate even if the sidebar is collapsed. The top Menu is deliberately independent of the native sidebar control because Streamlit does not expose an official Python API for programmatically reopening it.
- **Light and dark mode:** Use the **Dark mode** toggle at the top of the app. Its state is persisted in the URL (`?theme=dark`) through refreshes. Streamlit's default base theme remains light in `config.toml`; `ui_style.py` overrides the visible workspace colors. No need to restart when toggling.
- **Responsive layouts:** Smaller headings, flexible cards, wrapped sections, scrollable topic tables, and clearer radio choices on phones. No separate mobile install required.
- **IST display:** Saved sessions, attempt-history dates, and the progress-session table are shown in **Indian Standard Time (IST, UTC+05:30)**. Exported attempts CSV adds an `saved_at_ist` field alongside the original raw `created_at` timestamp. Existing SQLite records remain in UTC to preserve correct sorting and spaced-revision scheduling.
- **Safe backups:** The Progress page downloads a transaction-consistent SQLite online backup rather than copying a database file that could be mid-write.

## What stays compatible

All original question IDs, lecture packs, MCQ answer keys, coding challenges, notes, bookmarks, wrong-answer revision queues, session IDs, user profiles, and the SQLite database schema.

## If the sidebar's native open/close arrow is still missing

1. You can always use the app's top **Menu** to reach all six sections.
2. Make sure you replaced `app.py`, cleared your browser cache (hard refresh), and restarted Streamlit.
3. If your browser persisted an unusual sidebar state, try an incognito/private tab on `http://localhost:8501`; you can also clear site data for `localhost:8501` (this clears browser settings, **not** your SQLite progress file).
4. For best results, install the project's supported Streamlit version:
   `python -m pip install --upgrade "streamlit>=1.40,<2"`

## Validation

- Python files compile successfully.
- `pytest` passes 7 tests (including all six page paths, both color modes, answered/unanswered/completed quiz states, IST conversion, export, backup, menu navigation).
- Bundled CSS was checked in Chromium for 1440px and 390px viewport widths, including SVG icon loading, both mode backgrounds and horizontal overflow.
- **Limitation:** A real Streamlit browser session could not be run in the build environment because the Streamlit package was unavailable. The browser test used a static representative layout, not a live Streamlit runtime. If a browser-specific spacing issue remains, share a screenshot and Streamlit version so it can be adjusted precisely.
