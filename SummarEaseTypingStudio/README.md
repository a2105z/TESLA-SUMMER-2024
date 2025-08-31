# SummerEaseTypingStudio

**SummerEaseTypingStudio** is a Python desktop app that helps you **study smarter and type faster**:  
- 📚 **SummarEase Tab**: Load or paste an article, summarize it with AI (extractive by default, or OpenAI GPT if you set an API key).  
- ⌨️ **Typing Trainer Tab**: Practice typing on original or summarized text with live WPM, accuracy, streak, and high score tracking.  

Built with **Tkinter**, **SQLite**, and clean modular Python.  
Perfect as a portfolio project to showcase full-stack software engineering skills.

---

## Features
- 🔹 Summarize text from clipboard, file, or URL  
- 🔹 Offline extractive summarizer (no dependencies)  
- 🔹 Optional OpenAI summarizer if `OPENAI_API_KEY` is set  
- 🔹 Typing trainer with timer, pause/resume, per-character highlighting  
- 🔹 Tracks WPM, accuracy, streak, and global high score  
- 🔹 Persists texts & runs in `data/app.db`  
- 🔹 Unit tests with `pytest`  

---

## Project Structure
```

SummerEaseTypingStudio/
├─ app.py               # Tkinter entrypoint
├─ services/
│  ├─ summarizer.py     # Extractive + optional OpenAI summarizer
│  ├─ articles.py       # Load from file/URL/clipboard; sanitize
│  └─ storage.py        # SQLite: runs, texts, highscores
├─ ui/
│  ├─ typing\_tab.py     # TypingTrainerFrame
│  └─ summarize\_tab.py  # SummarEaseFrame
├─ data/
│  ├─ texts/            # Optional seed texts
│  └─ app.db            # SQLite DB auto-created on first run
├─ tests/
│  ├─ test\_summarizer.py
│  └─ test\_metrics.py
└─ logs/                # App logs

````

---

## Installation

### 1. Clone or download
```powershell
git clone https://github.com/yourusername/SummerEaseTypingStudio.git
cd SummerEaseTypingStudio
````

### 2. Create a virtual environment

**On Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**On macOS/Linux (bash/zsh):**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Your prompt should change to:

```
(.venv) PS C:\...\SummerEaseTypingStudio>
```

### 3. Install dev dependencies

```bash
pip install --upgrade pip
pip install pytest
```

*(no other dependencies required — Tkinter and SQLite are stdlib)*

---

## Running the App

```bash
python app.py
```

* SummarEase Tab → Paste text or load `.txt`, then click **Summarize**.
* Send Original/Summary → Typing Tab.
* Typing Trainer Tab → Click **Start**, type into the box, and watch WPM/accuracy live.

All results persist to `data/app.db`. Logs are in `logs/app.log`.

---

## Running Tests

```bash
pytest -q
```

You should see all tests pass:

```
.....                                                                 [100%]
```

---

## Optional: OpenAI API Key

If you want abstractive summarization via GPT:

**PowerShell (Windows):**

```powershell
$env:OPENAI_API_KEY="sk-xxxxx"
```

**bash/zsh (macOS/Linux):**

```bash
export OPENAI_API_KEY="sk-xxxxx"
```

Otherwise, the app uses the offline extractive summarizer.

---

## Example Screenshots (conceptual)

* **SummarEase Tab**: article in → summary out.
* **Typing Trainer Tab**: practice typing summary with live WPM/accuracy.

---

## License

MIT — free for personal & academic use.

---

## Author

Built with ❤️ as a software engineering project to showcase Python + UI + DB + AI integration.

---

👉 next step for you:  
- Save that as `README.md` in the project root.  
- Open PowerShell in your project folder and run:
  ```powershell
  python -m venv .venv
  .venv\Scripts\Activate.ps1
  pip install pytest
  python app.py
````