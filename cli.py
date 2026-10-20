#!/usr/bin/env python3
"""
SlothSync - Command Line Interface (CLI)
Empowering terminal power users to automate dreaded file organization lazily.
"""

import argparse
import sys
import time
from pathlib import Path
from sync_engine import SlothSyncEngine

BASE_DIR = Path(__file__).parent.resolve()


def print_banner():
    print("""
  🦥 SlothSync AI - Slow and Steady File Organization
  ---------------------------------------------------
  Rewarding laziness with local-first open-weight AI.
    """)


def main():
    parser = argparse.ArgumentParser(description="SlothSync: Autonomous file organizer and backup engine.")
    parser.add_argument("--source", default=str(BASE_DIR / "samples" / "messy_files"), help="Source folder to inspect")
    parser.add_argument("--backup", default=str(BASE_DIR / "samples" / "backup"), help="Destination backup folder")
    parser.add_argument("--scan", action="store_true", help="Perform dry-run scan and AI classification")
    parser.add_argument("--sync", action="store_true", help="Execute sync and categorize files into backup")
    parser.add_argument("--rollback", action="store_true", help="1-click rollback of latest sync session")
    parser.add_argument("--web", action="store_true", help="Launch interactive web dashboard")
    parser.add_argument("--port", type=int, default=8765, help="Port for web dashboard (default: 8765)")
    parser.add_argument("--watch", action="store_true", help="Continuously watch folder for changes")
    args = parser.parse_args()

    print_banner()

    if args.web:
        from app import run_server
        run_server(args.port)
        return

    engine = SlothSyncEngine(args.source, args.backup)

    if args.rollback:
        print("[*] Initiating 1-Click Rollback...")
        res = engine.rollback_last_sync()
        if res.get("status") == "success":
            print(f"[+] {res['message']} (Files reverted: {res['files_reverted']})")
        else:
            print(f"[-] {res['message']}")
        return

    if args.sync:
        print(f"[*] Executing SlothSync from '{args.source}' ➔ '{args.backup}'...")
        res = engine.execute_sync(organize_by_category=True)
        if res.get("status") == "success":
            print("\n[+] Sync Complete!")
            print(f"    Summary: {res['summary']}")
            print(f"    Files Synced: {res['actions_count']}")
            print(f"    Time Saved: ~{res['lazy_payoff']['minutes_saved']} minutes")
            print(f"    Manifest: {res['manifest']}")
        else:
            print(f"[-] Error: {res}")
        return

    if args.watch:
        print(f"[*] Watching '{args.source}' for changes (Debounce 5s)...")
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler

            class ChangeHandler(FileSystemEventHandler):
                def __init__(self, engine):
                    self.engine = engine
                    self.last_sync = 0

                def on_any_event(self, event):
                    now = time.time()
                    if now - self.last_sync > 5:
                        print(f"\n[!] Change detected: {event.src_path}. Syncing in background...")
                        self.engine.execute_sync()
                        self.last_sync = now

            observer = Observer()
            observer.schedule(ChangeHandler(engine), args.source, recursive=True)
            observer.start()
            print("[+] Watcher active. Press Ctrl+C to stop.")
            while True:
                time.sleep(1)
        except ImportError:
            print("[!] 'watchdog' package not found. Running periodic polling watch mode (every 10s)...")
            try:
                while True:
                    engine.execute_sync()
                    time.sleep(10)
            except KeyboardInterrupt:
                print("\nWatcher stopped.")
        except KeyboardInterrupt:
            print("\nWatcher stopped.")
        return

    # Default action: Scan & Dry Run
    print(f"[*] Scanning source folder: {args.source}")
    res = engine.scan()
    if "error" in res:
        print(f"[-] {res['error']}")
        return

    print(f"[+] AI Engine: {res['ai_engine']}")
    print(f"[+] Files Discovered: {res['file_count']} ({res['total_size_mb']} MB)")
    print(f"[+] Duplicates Caught: {res['duplicates_count']}")
    print(f"[+] The Lazy Payoff: Saved ~{res['lazy_payoff']['minutes_saved']} minutes of manual dread\n")
    print("Files Table:")
    print("-" * 75)
    print(f"{'Filename':<30} | {'Category':<12} | {'Suggested Name':<28}")
    print("-" * 75)
    for f in res["files"]:
        print(f"{f['name'][:28]:<30} | {f['category']:<12} | {f['suggested_name'][:26]:<28}")
    print("-" * 75)
    print(f"\nAI Summary:\n\"{res['summary']}\"")
    print("\nTip: Run with --sync to organize and backup, or --web to open the visual UI.")


if __name__ == "__main__":
    main()
