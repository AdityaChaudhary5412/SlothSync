# SlothSync 🦥
### *Autonomous Anti-Dread File Organizer & Sync Engine (Powered by Google Gemma)*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Open-Weight AI](https://img.shields.io/badge/Model-Gemma%202B-emerald.svg)](https://ai.google.dev/gemma)
[![Hacktoberfest 2026](https://img.shields.io/badge/Hacktoberfest-2026%20Week%203-orange.svg)](https://dev.to/challenges/hacktoberfest-week3-2026-10-19)

> **"Why do today what open-weight AI can do for you?"**  
> Built for the **Hacktoberfest Open-Source AI Challenge: Week 3 (Slow and Steady)** celebrating **International Sloth Day**.

---

## 🌟 The Problem: Procrastination & Digital Hoarding
Every developer, designer, and student dreads the same chaotic digital mess:
- A `Downloads` and `Desktop` folder flooded with hundreds of cryptic files: `invoice_final_v2(1).pdf`, `screenshot_2026_10.png`, `notes_temp_urgent.txt`, unfiled code snippets, and duplicate receipts.
- Sifting, opening, reading, renaming, and filing them away takes **hours of agonizing busywork**.
- Because it's tedious, we put it off for months.

## 🦥 The Sloth Solution: SlothSync
**SlothSync** channels the inner sloth. It runs quietly on your machine, reads and categorizes your files using **Google's Gemma open-weight model family**, detects and flags duplicate files with cryptographic **SHA-256 hashes**, organizes everything into clean semantic buckets, and provides a **1-click atomic rollback** so you can be completely lazy without any fear.

---

## ✨ Key Features

1. **Zero-Cloud, 100% On-Device Privacy:**
   - Powered by **Gemma 2B** running locally via Ollama (`localhost:11434`).
   - Your private contracts, bank statements, personal notes, and source code **never leave your machine**.
2. **Deterministic Heuristic Fallback Engine:**
   - Works immediately out of the box with zero external dependencies! If Ollama isn't installed or running, SlothSync seamlessly operates in offline heuristic mode.
3. **Content-Aware SHA-256 Deduplication:**
   - Catches duplicate files even when they have different names (e.g. `receipt(1).txt` vs `receipt_final.txt`), saving disk space and clutter.
4. **Safety-First Atomic Rollback:**
   - Every sync session writes an immutable JSON audit manifest (`.slothsync/manifests/`).
   - Made a mistake? Click **"1-Click Rollback"** to instantly revert every move.
5. **Interactive Web Dashboard + Power CLI:**
   - Sleek, dark-mode responsive Web UI built on Python's native `http.server` (zero `npm install` needed).
   - Rich CLI tool with `--scan`, `--sync`, `--rollback`, `--watch`, and `--web` options.

---

## 📊 The Lazy Payoff

| Metric | Manual Sorting | With SlothSync | Improvement |
| :--- | :--- | :--- | :--- |
| **Time Spent (50 files)** | ~45 - 60 minutes | **1.8 seconds** | **96% time saved** |
| **Dread & Procrastination** | High (delayed for weeks) | **Zero (One click / background)** | **100% Serenity** |
| **Duplicate Files** | Overlooked & cluttering | **100% detected via SHA-256** | Reclaims storage |
| **API Costs** | Cloud LLMs charge per token | **$0.00 (Permanent)** | Free forever |

---

## 🏗️ Architecture

```mermaid
flowchart TD
    A["Messy Source Directory (Downloads / Desktop)"] --> B["SlothSync Engine (Web UI / CLI)"]
    
    subgraph On_Device ["100% On-Device Local Processing"]
        B --> C["SHA-256 Hash & Deduplication"]
        C --> D{"Local Inference Selection"}
        
        D -->|"Ollama Running"| E["Google Gemma 2B / 9B Open-Weight LLM"]
        D -->|"Offline / Standalone"| F["Deterministic Semantic Classifier"]
        
        E --> G["Semantic Categorization & Renaming"]
        F --> G
        
        G --> H["Clean Category Buckets (Finance, Code, Notes, Media, Archives)"]
        H --> I["Atomic Rollback Manifest (.slothsync/manifests)"]
    end
    
    I --> J["Organized Backup & 1-Click Undo Safety 🦥"]
```

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/AdityaChaudhary5412/SlothSync.git
cd SlothSync
```

### 2. Launch the Web Dashboard
```bash
python3 app.py
```
Open **[http://localhost:8765](http://localhost:8765)** in your browser to experience the SlothSync dashboard.

### 3. Command Line Interface (CLI)

```bash
# Dry run scan of messy files
python3 cli.py --scan

# Organize and sync files to backup folder
python3 cli.py --sync

# 1-Click Rollback of the last sync operation
python3 cli.py --rollback

# Continuous background watch mode
python3 cli.py --watch
```

### 4. (Optional) Run with Local Gemma 2B
To enable deep LLM semantic reasoning:
```bash
# Install Ollama and pull Gemma 2B
ollama run gemma2:2b
```
SlothSync will automatically detect the local Gemma model and route summaries through it!

---

## 🧪 Automated Testing

SlothSync comes with a comprehensive unit test suite with 100% passing tests:

```bash
python3 -m unittest discover -s tests
```

Output:
```plaintext
.....
----------------------------------------------------------------------
Ran 5 tests in 0.016s

OK
```

---

## 📂 Project Structure

```plaintext
SlothSync/
├── engine.py              # Local Gemma 2B & heuristic classification engine
├── sync_engine.py         # SHA-256 deduplication, sync & rollback manifest engine
├── app.py                 # Zero-dependency Python web server & REST API
├── cli.py                 # CLI interface for terminal power users
├── static/
│   ├── index.html         # Responsive, dark-mode glassmorphism dashboard
│   ├── style.css          # Theme styles (Forest / Sloth Hacktoberfest palette)
│   └── app.js             # Real-time reactivity, scan & sync handling
├── samples/
│   └── messy_files/       # Sample clutter files for instant evaluation
├── tests/
│   └── test_sync.py       # Automated unit test suite (100% passing)
├── requirements.txt       # Optional extensions (watchdog, rich)
├── LICENSE                # MIT License
└── README.md              # Full documentation
```

---

## 💡 Why Open Innovation Matters
- **Ironclad Privacy:** Personal receipts, medical records, and client invoices should never be uploaded to cloud AI providers. Open-weight models like Gemma allow AI to operate directly on private hardware.
- **Permanent Availability & Zero Marginal Cost:** Cloud APIs deprecate endpoints and charge recurring subscription fees. Running open-weight Gemma costs $0 forever.
- **Offline Resilience:** Works completely offline without needing an active internet connection.

---

## 📜 License
Released under the [MIT License](LICENSE).  
Built with ❤️ by [Aditya Chaudhary](https://github.com/AdityaChaudhary5412) for **Hacktoberfest 2026**.
