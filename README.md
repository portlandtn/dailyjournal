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
- Uses OpenAI only for **structured guidance** (no rambling, no journaling for you)

---

## Requirements

- Python **3.10+**
- An OpenAI API key
- macOS, Linux, or Windows

---

## Installation (Recommended: pipx)

The easiest way to use `dailyjournal` as a real CLI (no virtual environments):

### 1. Install pipx

macOS (Homebrew):
```bash
brew install pipx
pipx ensurepath
```

Restart your terminal after this.

---

### 2. Install dailyjournal

From the repo root:

```bash
pipx install .
```

Or, if you are actively developing:

```bash
pipx install -e .
```

This installs the `dailyjournal` command globally for your user.

---

## Environment Variables

`dailyjournal` relies on environment variables for configuration.

### Required

```bash
export OPENAI_API_KEY="your_api_key_here"
```

### Recommended paths

Using per-user local DB + iCloud for sync:

```bash
export DAILYJOURNAL_DB_PATH="$HOME/Library/Application Support/dailyjournal/coachscribe.db"
export DAILYJOURNAL_SYNC_DIR="$HOME/Library/Mobile Documents/com~apple~CloudDocs/dailyjournal/entries"
```

Add these to `~/.zshrc` or `~/.zprofile`.

---

## Usage

### Show help

```bash
dailyjournal help
```

---

### Morning session (AM)

```bash
dailyjournal am
```

Prompts you to:
- Define one concrete **work outcome**
- Define one small **personal/family win**
- Identify what is most likely to derail you today
- Create an **if-then plan** for stress or distraction
- Add optional **additional notes** (free-text)

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
- The database is **ignored by Git**
- Entries are also exported as append-only JSON files for optional cross-machine sync
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
