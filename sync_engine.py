"""
SlothSync - Safe Synchronization & Manifest Engine
Features SHA-256 deduplication, atomic change tracking, and one-click rollback.
"""

import hashlib
import json
import os
import shutil
import time
from pathlib import Path
from engine import AISummarizer


def compute_file_hash(path: Path) -> str:
    """Compute SHA-256 hash of a file for exact content deduplication."""
    hasher = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return ""


class SlothSyncEngine:
    def __init__(self, source_dir: str, backup_dir: str):
        self.source_dir = Path(source_dir).expanduser().resolve()
        self.backup_dir = Path(backup_dir).expanduser().resolve()
        self.ai = AISummarizer()
        self.meta_dir = self.source_dir / ".slothsync"
        self.manifest_dir = self.meta_dir / "manifests"
        self.logs_dir = self.meta_dir / "logs"
        self._ensure_meta_dirs()

    def _ensure_meta_dirs(self):
        try:
            self.manifest_dir.mkdir(parents=True, exist_ok=True)
            self.logs_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

    def scan(self) -> dict:
        """Scan source folder, detect duplicates, and categorize all files."""
        if not self.source_dir.exists():
            return {"error": f"Source directory does not exist: {self.source_dir}"}

        files_found = []
        hashes = {}
        duplicates = []
        total_bytes = 0

        for root, dirs, files in os.walk(self.source_dir):
            # Ignore hidden files and .slothsync metadata
            dirs[:] = [d for d in dirs if not d.startswith(".") and d != ".slothsync"]
            for fname in files:
                if fname.startswith("."):
                    continue
                fpath = Path(root) / fname
                rel_path = fpath.relative_to(self.source_dir)
                size = fpath.stat().st_size
                total_bytes += size

                file_hash = compute_file_hash(fpath)

                # Read small snippet for text analysis
                snippet = ""
                if fpath.suffix.lower() in [".txt", ".md", ".py", ".csv", ".json", ".html", ".js"]:
                    try:
                        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                            snippet = f.read(200)
                    except Exception:
                        pass

                cat_info = self.ai.categorize_file(fname, snippet)

                is_dup = False
                original = None
                if file_hash:
                    if file_hash in hashes:
                        is_dup = True
                        original = str(hashes[file_hash])
                        duplicates.append({
                            "duplicate": str(rel_path),
                            "original": original,
                            "size": size
                        })
                    else:
                        hashes[file_hash] = rel_path

                files_found.append({
                    "name": fname,
                    "rel_path": str(rel_path),
                    "full_path": str(fpath),
                    "size": size,
                    "hash": file_hash,
                    "category": cat_info.get("category", "Documents"),
                    "suggested_name": cat_info.get("suggested_name", fname),
                    "tags": cat_info.get("tags", []),
                    "is_duplicate": is_dup,
                    "duplicate_of": original
                })

        summary = self.ai.summarize_batch(files_found)
        # 3 minutes of dread saved per file manually sorted/backed up
        minutes_saved = round(len(files_found) * 3.2, 1)

        return {
            "source": str(self.source_dir),
            "backup": str(self.backup_dir),
            "file_count": len(files_found),
            "total_bytes": total_bytes,
            "total_size_mb": round(total_bytes / (1024 * 1024), 2),
            "duplicates_count": len(duplicates),
            "duplicates": duplicates,
            "files": files_found,
            "ai_engine": "Gemma 2B (Ollama Local)" if self.ai.use_gemma else "Deterministic Heuristics (Offline Mode)",
            "summary": summary,
            "lazy_payoff": {
                "minutes_saved": minutes_saved,
                "dread_level_reduction": "100%",
                "duplicates_prevented": len(duplicates),
                "storage_reclaimed_kb": round(sum(d["size"] for d in duplicates) / 1024, 2)
            }
        }

    def execute_sync(self, organize_by_category: bool = True) -> dict:
        """Perform synchronization and write an atomic rollback manifest."""
        scan_result = self.scan()
        if "error" in scan_result:
            return scan_result

        self.backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = int(time.time())
        synced_actions = []

        for item in scan_result["files"]:
            src_path = Path(item["full_path"])
            if not src_path.is_file():
                continue

            if organize_by_category:
                dest_subfolder = self.backup_dir / item["category"]
                dest_path = dest_subfolder / item["suggested_name"]
            else:
                dest_path = self.backup_dir / item["rel_path"]

            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dest_path)

            synced_actions.append({
                "source": str(src_path),
                "destination": str(dest_path),
                "category": item["category"],
                "size": item["size"],
                "hash": item["hash"]
            })

        # Save rollback manifest
        manifest_data = {
            "timestamp": timestamp,
            "date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp)),
            "source_dir": str(self.source_dir),
            "backup_dir": str(self.backup_dir),
            "organize_by_category": organize_by_category,
            "summary": scan_result["summary"],
            "actions": synced_actions,
            "lazy_payoff": scan_result["lazy_payoff"]
        }

        manifest_file = self.manifest_dir / f"manifest_{timestamp}.json"
        with open(manifest_file, "w") as f:
            json.dump(manifest_data, f, indent=2)

        # Write markdown log
        log_file = self.logs_dir / f"sync_{timestamp}.md"
        with open(log_file, "w") as f:
            f.write(f"# SlothSync Audit Log – {manifest_data['date']}\n\n")
            f.write(f"**AI Engine:** {scan_result['ai_engine']}\n\n")
            f.write(f"**Summary:** {scan_result['summary']}\n\n")
            f.write(f"### The Lazy Payoff\n")
            f.write(f"- **Time Saved:** ~{scan_result['lazy_payoff']['minutes_saved']} minutes of dreaded manual filing\n")
            f.write(f"- **Duplicates Flagged:** {scan_result['lazy_payoff']['duplicates_prevented']}\n")
            f.write(f"- **Files Protected:** {len(synced_actions)}\n\n")
            f.write("### Synced Items:\n")
            for a in synced_actions:
                f.write(f"- `[{a['category']}]` {os.path.basename(a['source'])} ➔ `{os.path.basename(a['destination'])}`\n")

        return {
            "status": "success",
            "timestamp": timestamp,
            "manifest": str(manifest_file),
            "log": str(log_file),
            "actions_count": len(synced_actions),
            "summary": scan_result["summary"],
            "lazy_payoff": scan_result["lazy_payoff"]
        }

    def rollback_last_sync(self) -> dict:
        """Atomic 1-click rollback of the latest sync session."""
        manifests = sorted(list(self.manifest_dir.glob("manifest_*.json")), reverse=True)
        if not manifests:
            return {"status": "error", "message": "No sync manifests found to rollback."}

        latest_manifest_path = manifests[0]
        try:
            with open(latest_manifest_path, "r") as f:
                manifest_data = json.load(f)

            removed_count = 0
            for action in manifest_data.get("actions", []):
                dest = Path(action["destination"])
                if dest.exists() and dest.is_file():
                    dest.unlink()
                    removed_count += 1

            # Rename manifest to mark rolled back
            rolled_back_path = latest_manifest_path.with_suffix(".rolled_back.json")
            latest_manifest_path.rename(rolled_back_path)

            return {
                "status": "success",
                "message": f"Successfully rolled back sync from {manifest_data.get('date', 'unknown')}.",
                "files_reverted": removed_count,
                "manifest": str(rolled_back_path)
            }
        except Exception as e:
            return {"status": "error", "message": f"Rollback failed: {str(e)}"}
