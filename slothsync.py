import argparse, shutil, time, os
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, batch, interval=5):
        self.batch = batch
        self.interval = interval
        self.last_event = time.time()
    def on_any_event(self, event):
        now = time.time()
        self.batch.append(event.src_path)
        self.last_event = now

def summarise_changes(paths):
    # Placeholder – in a real version we call local Gemma via Ollama
    return f"Detected {len(paths)} file changes: " + ", ".join([os.path.basename(p) for p in paths[:5]])

def sync_files(paths, backup_dir):
    for p in set(paths):
        src = Path(p)
        if src.is_file():
            # Preserve relative path from the root directory being watched
            # Assuming watch_dir is a parent of src
            rel = src.relative_to(src.anchor)
            dst = Path(backup_dir) / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

def main(watch_dir, backup_dir):
    batch = []
    handler = ChangeHandler(batch)
    observer = Observer()
    observer.schedule(handler, watch_dir, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
            if batch and time.time() - handler.last_event > handler.interval:
                summary = summarise_changes(batch)
                log_dir = Path(watch_dir) / ".slothsync" / "logs"
                log_dir.mkdir(parents=True, exist_ok=True)
                (log_dir / f"{int(time.time())}.md").write_text(summary)
                sync_files(batch, backup_dir)
                batch.clear()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--watch", required=True, help="Directory to watch for changes")
    parser.add_argument("--backup", required=True, help="Backup destination directory")
    args = parser.parse_args()
    main(args.watch, args.backup)
