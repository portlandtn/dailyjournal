# dailyjournal

A **local-first**, CLI-based AM/PM journaling tool focused on **intentional work, accountability, and follow-through**.

`dailyjournal` is designed to help you:
- Set **one clear work priority** and **one personal/family priority** each day
- Anticipate distraction and stress before they derail you
- Review execution honestly at night
- Carry momentum from one day to the next
- Keep your journal data **under your control**

No dashboards. No gamification. No therapy bot. Just structure.

---

## Features

- Morning (AM) intention setting
- Evening (PM) accountability and review
- Explicit recall of your own commitments
- Optional free-text notes (AM & PM)
- Mid-day append notes (`append`)
- Local SQLite storage
- Append-only JSON exports for safe cross-machine sync
- Simple, fast CLI interface
- Uses OpenAI only for **structured guidance** (no rambling)

---

## Requirements

- Python **3.10+**
- An OpenAI API key
- macOS, Windows, or Linux

---

## Installation (Recommended: pipx)

`pipx` installs Python CLI tools in isolated environments and makes them globally available
without requiring virtual environments or polluting system Python.

---

### macOS

#### 1. Install pipx
```bash
brew install pipx
pipx ensurepath
```
Restart your terminal after this step.

#### 2. Install dailyjournal
```bash
pipx install jeds-dailyjournal
```

---

### Windows

#### 1. Install pipx
```powershell
py -m pip install --user pipx
py -m pipx ensurepath
```
Open a **new PowerShell window** after this step.

#### 2. Install dailyjournal
```powershell
pipx install jeds-dailyjournal
```

---

### Linux

#### 1. Install pipx
```bash
python3 -m pip install --user pipx
pipx ensurepath
```
Restart your terminal or re-source your shell config.

#### 2. Install dailyjournal
```bash
pipx install jeds-dailyjournal
```

---

## Initial Setup (Wizard)

After installation, run the setup wizard once:

```bash
dailyjournal setup
```

The wizard will:
- Ask where to store your local SQLite database
- Ask where to export/backup JSON entry files
- Ask which OpenAI model to use (default is fine)
- Prompt for your OpenAI API key

### 🔐 API Key Storage (Secure)
Your OpenAI API key is stored securely using the operating system's credential store:
- **macOS:** Keychain
- **Windows:** Credential Manager
- **Linux:** Secret Service / keyring backend

The key is **not stored in plaintext** and does **not** require environment variables.

---

## Usage

### Show help
```bash
dailyjournal help
```

### Morning session (AM)
```bash
dailyjournal am
```

Prompts you to:
- Define one concrete **work outcome**
- Define one small **personal/family win**
- Identify likely sources of distraction
- Create an **if–then plan**
- Add optional free-text notes

---

### Append a note during the day
```bash
dailyjournal append "Meeting moved to 3pm"
```
or interactive mode:
```bash
dailyjournal append
```

Append notes are:
- Stored locally
- Exported as immutable JSON
- Included automatically in the PM review

---

### Evening session (PM)
```bash
dailyjournal pm
```

Reviews:
- Whether you completed what you committed to
- What actually caused distraction
- One adjustment for tomorrow
- Sets a **tomorrow focus** carried into the next AM
- Allows additional free-text notes

Your AM notes and append notes are surfaced and fed into the PM analysis.

---

### View recent summaries
```bash
dailyjournal last
```

---

### Version
```bash
dailyjournal --version
dailyjournal -V
```

---

## Data & Privacy

- All journal entries are stored locally in a SQLite database:
  ```
  coachscribe.db
  ```
- The database is ignored by Git
- Entries are also exported as append-only JSON files for optional backup or sync
- Nothing is uploaded or shared automatically
- You control all of your data

Deleting the database removes local history; JSON exports remain if you keep them.

---

## Project Structure

```
dailyjournal/
├── app.py           # CLI entry point
├── coach.py         # OpenAI interaction layer
├── prompts.py       # Prompt rails and questions
├── store.py         # SQLite persistence
├── entries.py       # JSON export / sync helpers
├── config.py        # Config loading/saving
├── dj_secrets.py    # Secure credential access
├── pyproject.toml
├── .gitignore
└── coachscribe.db   # (local only, ignored)
```

---

## Philosophy

- Minimal by design
- Behavior > features
- Explicit commitments beat vague intentions
- Reflection only matters if it affects tomorrow

Use it daily for a week before changing anything.

---

## License
Private / personal use.
