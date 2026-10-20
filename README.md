# SlothSync

**SlothSync** is a lightweight, local‑first AI‑powered file synchronization and backup tool that helps you *automatically* keep your important documents in sync across multiple devices *without ever sending your data to the cloud*.

## Why SlothSync?
- **Privacy first** – All AI inference runs on‑device using an open‑weight model (e.g., `gemma2:2b` via Ollama). No data ever leaves your machine.
- **Zero cost** – No per‑request API fees. The only requirement is a local model runner.
- **Save time** – Detects new or changed files, generates concise change summaries, and can even suggest better folder structures.

## Features
- Watch one or more directories for changes (create, modify, delete).
- Summarise changes with a local LLM and store the summary in a hidden `.slothsync` log.
- Sync the changes to a user‑specified backup location (USB drive, external HDD, or another folder).
- Simple CLI with optional TUI (text UI) powered by `rich`.

## Quick Start
```bash
# Install Ollama and the Gemma 2B model (once)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull gemma2:2b

# Clone the repository and install dependencies
git clone https://github.com/YourUsername/slothsync.git
cd slothsync
pip install -r requirements.txt

# Run SlothSync – watch ~/Documents and backup to /Volumes/BackupDrive
python3 slothsync.py --watch ~/Documents --backup /Volumes/BackupDrive
```

## How It Works
1. **File Watcher** – Uses `watchdog` to monitor filesystem events.
2. **Change Collector** – Accumulates a batch of events (debounced 5 s).
3. **LLM Summariser** – Sends a concise description of the batch to the local Gemma model.
4. **Sync Engine** – Copies changed files to the backup location while preserving timestamps.
5. **Log** – Stores the LLM summary in `.slothsync/logs/<timestamp>.md`.

## Architecture
```mermaid
flowchart TD
    A[File System] -->|watchdog| B[Event Collector]
    B --> C[Batch (5s)]
    C --> D[Local Gemma Summariser]
    D --> E[Change Summary]
    C --> F[Sync Engine]
    F --> G[Backup Destination]
    E --> H[Log (.slothsync)]
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style G fill:#bbf,stroke:#333,stroke-width:2px
```

## License
MIT – feel free to fork, improve, and share!

---

*This project was built for the **Hacktoberfest Open‑Source AI Challenge: Week 3 – Slow and Steady**.*
