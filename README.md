# Python Mastery Lab

**Upgrade existing installations:** Use the UI-only ZIP and follow [UI_UPGRADE_GUIDE.md](UI_UPGRADE_GUIDE.md). Copy `app.py`, **new** `ui_style.py`, and `.streamlit/config.toml` only; preserve `data/progress.sqlite3`, question packs, and `quiz_core.py`.

The top **Dark mode** switch remembers its state via the page URL; the top **Menu** always provides navigation even when the sidebar is collapsed. All displayed saved dates use **IST** (UTC+05:30) while SQLite records stay in UTC for correct spaced-revision logic.

# 🐍 Python Mastery Lab — Lecture 1

> **New visual redesign (v2):** The app now has a modern light workspace, dark sidebar, upgraded quiz controls, clearer revision queues, and responsive layouts. If you're **upgrading** an existing installation, follow [UI_UPGRADE_GUIDE.md](UI_UPGRADE_GUIDE.md) to keep `data/progress.sqlite3` and all your packs. Do **not** replace your progress database.

**201 MCQs + 28 hands-on coding challenges** based on the supplied *Python Notes (Lecture 1)* (12 pages), plus clearly marked advanced/interview extensions.

A local, interactive study app made for learners who use **VS Code**. Quiz progress lives in a **SQLite database on your own computer**. The app does not call an AI service, requires no account, and does not upload your code for execution.

## 1. Start the app in VS Code

1. Unzip `Python_Mastery_Lab_Lecture_1.zip` to a folder you plan to keep.
2. Open that folder in **VS Code** (`File → Open Folder`).
3. Open VS Code's terminal (`Terminal → New Terminal`).
4. Use these commands:

**Windows PowerShell**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Streamlit opens the quiz in your browser (normally `http://localhost:8501`). Keep the terminal running while studying. To stop, press `Ctrl+C`. Later, reactivate the virtual environment and run only `python -m streamlit run app.py`.

**Requirements:** Python 3.10+ recommended, internet once for installing Streamlit, and any current browser. The quiz operates locally after installation.

**No external installation available?** You can start a simpler interactive MCQ version directly in the VS Code terminal with `python terminal_quiz.py`. The terminal mode uses the **same SQLite question/answer history** and supports mixed quizzes, missed-question review, due review, explanations and saved-session resume. The full coding dojo and analytics require the Streamlit browser interface.

## 2. How to use it

| Page | What it does |
|---|---|
| 🏠 Overview | Open a quick 15-question Smart Mix session; see quiz and coding counts. |
| 🧠 Quiz arena | Topic/level/lecture filters; one MCQ at a time, explanations and immediate results, save/resume. |
| 🛠️ Coding dojo | Try practical problems in VS Code, run the examples yourself, save draft, reveal hint/solution, self-grade. |
| 🗂️ Review lab | Retry missed/due/bookmarked questions. View previous incorrect options and explanations. |
| 📊 Progress | Topic-level performance, accuracy, session history, full attempts CSV and SQLite backup. |
| 📦 Question packs | Show installed lectures; import additional validated JSON question packs. |

### Quiz modes

- **Smart Mix:** prioritizes questions with the last answer wrong, then questions due for review, then previously unseen questions.
- **All:** random set from your filters.
- **Unseen:** never answered/graded before.
- **Missed:** your most recent attempt was incorrect.
- **Due:** previously answered questions with a revision date reached.
- **Bookmarked:** questions you saved manually.

Every MCQ has **four options**, a stored correct answer and an explanation. Once submitted, you see the right option and the reasoning. You cannot alter a submitted answer in that session; retry by starting a new session.

After a *correct* response, that question is scheduled again in **1, 3, 7, 14, 30, 60 or 90 days** depending on your consecutive success streak. After a *wrong* response, it is marked immediately due. Previous attempts **are never erased** when you eventually answer correctly.

### Coding problems and VS Code

Open **Coding dojo**, select a problem, then write a `.py` file in VS Code and test it with the supplied sample inputs. Paste your code into the in-app draft field when you want to save a copy. Optionally open the hint, reveal the reference solution, and mark *Solved independently* or *Need more practice*.

**Important:** The app does **not** automatically execute or assess pasted code. Coding results are self-reported. This keeps your code execution inside VS Code and makes it easy to examine failing edge cases yourself.

## 3. Lecture topics and question coverage

The 14 lecture topics are:

1. Programming, machine code, compiler and interpreter (page 1)
2. Python characteristics and portability (page 1)
3. `print()` and output (pages 1–2)
4. Python character set, whitespace and Unicode (page 2)
5. Variables, values and reassignment (pages 2–3)
6. Valid identifiers, keywords and case sensitivity (page 3)
7. Built-in data types, `None`, complex and `type()` (pages 3–4)
8. Python reserved keywords (pages 4–5)
9. Sum, square area and averages (pages 5, 11–12)
10. Single-line comments and triple-quoted strings (pages 5–6)
11. Arithmetic, relational, assignment and logical operators (pages 6–8)
12. Implicit type conversion (page 8)
13. Explicit casting with `int`, `float`, `str`, `bool`, `complex`, `list`, `tuple`, `set`, `dict`, `ord`, `hex`, `oct` (pages 8–10)
14. `input()` with string/int/float and all four practice questions (pages 10–12)

In every question, **“PDF material”** means it targets ideas demonstrated or listed in the uploaded lecture; **“Advanced extension”** means it deliberately goes beyond the lecture. Extensions include common traps such as `2**3**2`, `-3**2`, negative modulo and floor division, 0.1+0.2, `True + True`, truthiness of `'False'`, short-circuit return values, `is` vs `==`, `int(-3.9)`, Unicode identifiers, float rounding, and conversion errors.

### Two useful technical nuances

- The notes contrast **compilers vs. interpreters** in a beginner-friendly way. In CPython, source is normally compiled to **bytecode** and then executed by a Python virtual machine. Questions introducing this detail are marked as extensions.
- The notes call triple-quoted text a “multi-line comment.” Triple quotes actually create **string literals**; in docstring positions they become **docstrings**. True Python comments use `#`. The distinction is called out in extension questions.

## 4. How saved sessions work

All state is stored in **`data/progress.sqlite3`**, which is created automatically when you first run the app. It contains quiz sessions, wrong/correct attempts, a simple spaced-review schedule, profile-specific personal notes, bookmarks and your coding drafts. Unfinished sessions are listed at the top of the quiz page. Pick the same **Learner profile** name whenever you return.

**Do not delete `data/progress.sqlite3`** when upgrading the app or adding more lectures. Back it up using **Progress → Back up full progress database** (prefer doing so after you finish active actions; stop the app for a guaranteed consistent file-level copy).

The packaged `data` folder is intentionally empty. Your real progress begins when *you* run the app; the shipped quiz does not come with someone else's scores.

## 5. How we extend this when you send another PDF

1. Send the new PDF with a request to create a second **Python Mastery Lab question pack**, maintaining this app's JSON schema.
2. The new bank receives a **unique `pack_id`** (`lecture-2`, `lecture-3`, etc.) and globally unique IDs (`L2-M001`, `L2-C001`, etc.).
3. Place the new JSON inside `packs/` **or** import it from **Question packs → Import**.
4. Restart/refresh the app. Both lectures become selectable while prior scores remain untouched.

The app imports **JSON question packs**, not raw PDFs. Your future PDF must be analyzed and turned into a question pack first. The UI includes a JSON template.

## 6. Optional tests

The project also ships standard validation tests. Install pytest (`python -m pip install pytest`) then run:

```bash
python -m pytest -q
```

The tests check pack structure, coverage, duplicate answers, resuming sessions, stored wrong answers, repeated attempts, notes/bookmarks, and code-draft persistence.

## Folder map

```text
python_mastery_lab/
├── app.py                  # Streamlit browser UI
├── terminal_quiz.py        # No-dependency, interactive terminal fallback
├── quiz_core.py            # SQLite persistence + question selection
├── packs/
│   └── lecture_1.json      # All MCQs, explanations, solutions and references
├── reference/
│   └── python-notes-lecture-1.pdf
├── data/                   # progress.sqlite3 is created here on first launch
├── tests/
│   └── test_quiz_core.py
├── .streamlit/
│   └── config.toml         # App color theme
├── requirements.txt
└── README.md
```

Enjoy practicing — revisit explanations and try to explain the *wrong* choices, too.

## Reference material for advanced extensions

The advanced traps have been cross-checked against Python’s official [expression/precedence reference](https://docs.python.org/3/reference/expressions.html) and [floating-point tutorial](https://docs.python.org/3/tutorial/floatingpoint.html). The original lecture PDF is included in `reference/`.
