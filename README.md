# Datheon Python Programming Internship

**Verified Internship Project Submission**

This repository contains all completed tasks for the **Datheon Python Programming Internship**. Each task demonstrates practical Python skills including file I/O, data processing, automation, and interactive applications.

---

## Project Structure

```
Datheon_Python_Programming_Internship/
│
├── task1_hangman/
│   ├── hangman.py          # Terminal-based Hangman game
│   └── words.txt           # English word list (~8,000 words)
│
├── task2_portfolio/
│   ├── portfolio.py        # Stock portfolio performance tracker
│   └── constituents.csv    # S&P 500 ticker reference list
│
├── task3_organizer/
│   └── organizer.py        # Automated file organizer utility
│
├── task4_chatbot/
│   ├── chatbot.py          # Rule-based interactive chatbot
│   └── sample_faq.json     # FAQ knowledge base
│
└── README.md
```

---

## Task Overview

### Task 1 — Terminal Hangman Game
A classic Hangman implementation with:
- Random word selection from a large English word list
- ASCII-art gallows that updates on each incorrect guess
- Tracking of previously guessed letters (no double penalty)
- 6-mistake limit and win/lose detection
- Replay support

**Run:**
```bash
cd task1_hangman
python hangman.py
```

---

### Task 2 — Stock Portfolio Performance Tracker
An interactive portfolio utility that:
- Accepts ticker symbols, share quantities, and buy prices
- Fetches **live market prices** via `yfinance`
- Calculates invested capital, current value, and gain/loss ($ and %)
- Validates tickers against an S&P 500 constituents list
- Logs performance snapshots to `portfolio_summary.csv`
- Optionally persists holdings to `portfolio_positions.csv`

**Requirements:**
```bash
pip install yfinance
```

**Run:**
```bash
cd task2_portfolio
python portfolio.py
```

---

### Task 3 — Automated File Organizer
A desktop cleanup utility that:
- Scans a target directory (default: `~/Downloads`)
- Maps 70+ file extensions to categories (Documents, Images, Videos, Audio, Archives, Code, etc.)
- Creates category subfolders and moves files safely
- Handles naming collisions and permission errors
- Supports dry-run preview mode

**Run:**
```bash
cd task3_organizer
python organizer.py                    # interactive
python organizer.py ~/Downloads        # specific folder
python organizer.py ~/Downloads -n     # dry-run only
```

---

### Task 4 — Rule-Based Interactive Chatbot
A conversational internship support assistant that:
- Loads FAQs and greetings from JSON
- Performs multi-intent recognition using regex + keyword scoring
- Handles hours, project submission, certificates, help, thanks, and date/time
- Provides graceful fallbacks for unrecognized queries
- Clean exit on `bye` / `exit` / `quit`

**Run:**
```bash
cd task4_chatbot
python chatbot.py
```

---

## Requirements

- **Python 3.8+**
- Task 2 only: `yfinance` (`pip install yfinance`)
- All other tasks use the Python standard library only

---

## How to Submit

1. Create a **public** GitHub repository named exactly:
   ```
   Datheon_Python_Programming_Internship
   ```
2. Push this project (source code + README) to the repository.
3. Paste the public repository URL into the Datheon submission form.
4. (Optional) Share a screenshot or short demo on LinkedIn and tag **@Datheon**.

---

## Author

Completed as part of the Datheon Python Programming Internship program.
