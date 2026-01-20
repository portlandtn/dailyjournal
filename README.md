# dailyjournal

A local-first, CLI-based AM/PM journaling tool focused on **intentional work, accountability, and follow-through**.

This tool is designed to:
- Set **one clear work priority** and **one family/personal priority** each day
- Reduce distraction (especially phone usage)
- Review execution honestly at night
- Carry momentum from one day to the next
- Keep all journal data **local to your machine**

No cloud sync. No dashboards. No therapy bot. Just structure.

---

## Features

- Morning (AM) intention setting
- Evening (PM) accountability and review
- Explicit recall of your own commitments
- Local SQLite storage (nothing leaves your machine)
- Simple CLI interface
- Uses OpenAI only for structured guidance (no free-form rambling)

---

## Requirements

- Python **3.10+**
- An OpenAI API key
- macOS, Linux, or Windows

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/portlandtn/dailyjournal.git
cd dailyjournal
```

---

### 2. Create and activate a virtual environment

#### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Windows (PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Install the CLI command (editable mode)

```bash
pip install -e .
```

This creates the `dailyjournal` command.

---

## Environment Variables

The app requires an OpenAI API key, stored as an environment variable.

### macOS / Linux (zsh)

Add this to `~/.zshrc`:

```bash
export OPENAI_API_KEY="your_api_key_here"
```

Then reload:

```bash
source ~/.zshrc
```

---

### Windows (PowerShell)

Set it permanently:

```powershell
setx OPENAI_API_KEY "your_api_key_here"
```

Open a **new** terminal after running this.

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
- Define one concrete work outcome
- Define one small personal/family win
- Set a focus/phone guardrail
- Create an if-then plan for stress or distraction

---

### Evening session (PM)

```bash
dailyjournal pm
```

Reviews:
- Whether you completed what you said you would
- What derailed you (if anything)
- One adjustment for tomorrow
- Sets a “tomorrow focus” carried into the next morning

---

### View recent summaries

```bash
dailyjournal last
```

---

## Data & Privacy

- All journal entries are stored locally in a SQLite database:
  ```
  coachscribe.db
  ```
- This file is **ignored by Git** and never committed
- Nothing is uploaded or synced automatically
- You control your data completely

If you delete the database file, all journal history is removed.

---

## Project Structure

```
dailyjournal/
├── app.py           # CLI entry point
├── coach.py         # OpenAI interaction layer
├── prompts.py       # Prompt rails and questions
├── store.py         # SQLite persistence
├── requirements.txt
├── pyproject.toml
├── .gitignore
└── coachscribe.db   # (local only, not committed)
```

---

## Notes

- This tool is intentionally minimal.
- It favors **behavior change over features**.
- Use it for a few days before modifying prompts or flow.

---

## License

Private / personal use (add a license if you plan to distribute).
