"""
SlothSync - AI Summarization & Semantic Categorization Engine
Integrates locally with Google's open-weight Gemma models via Ollama.
Includes a robust deterministic fallback engine when running fully offline.
"""

import json
import os
import re
import urllib.request
import urllib.error
from pathlib import Path


class AISummarizer:
    def __init__(self, ollama_url="http://localhost:11434", model="gemma2:2b"):
        self.ollama_url = ollama_url.rstrip("/")
        self.model = model
        self.use_gemma = self._check_ollama_status()

    def _check_ollama_status(self) -> bool:
        """Check if local Ollama daemon is reachable and has Gemma available."""
        try:
            req = urllib.request.Request(f"{self.ollama_url}/api/tags", headers={"User-Agent": "SlothSync"})
            with urllib.request.urlopen(req, timeout=1.2) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode())
                    available_models = [m.get("name", "") for m in data.get("models", [])]
                    # Check for gemma in installed models
                    for m in available_models:
                        if "gemma" in m.lower():
                            self.model = m
                            return True
                    return len(available_models) > 0
        except Exception:
            pass
        return False

    def query_gemma(self, prompt: str) -> str:
        """Query local Gemma model with low latency and zero data leakage."""
        if not self.use_gemma:
            return ""
        try:
            payload = json.dumps({
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "top_p": 0.9,
                    "num_predict": 128
                }
            }).encode("utf-8")

            req = urllib.request.Request(
                f"{self.ollama_url}/api/generate",
                data=payload,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=8.0) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode())
                    return data.get("response", "").strip()
        except Exception:
            self.use_gemma = False
        return ""

    def categorize_file(self, filename: str, sample_text: str = "") -> dict:
        """Categorize a file into a clean semantic bucket with tags."""
        ext = Path(filename).suffix.lower()
        base = Path(filename).stem.lower()

        # Try Gemma if available
        if self.use_gemma:
            prompt = (
                f"You are SlothSync, an AI organizing files. Given filename: '{filename}' "
                f"and snippet: '{sample_text[:120]}'. Output JSON with keys: category (one of: Documents, Code, "
                f"Finance, Media, Archives, Notes), suggested_name (clean lowercase name with extension), and tags (list of 2 tags)."
            )
            resp = self.query_gemma(prompt)
            match = re.search(r"\{.*\}", resp, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except Exception:
                    pass

        # Deterministic Heuristic Engine Fallback
        return self._heuristic_categorization(filename, ext, base, sample_text)

    def _heuristic_categorization(self, filename: str, ext: str, base: str, sample_text: str) -> dict:
        """Deterministic, zero-dependency classification engine."""
        category = "Documents"
        tags = ["file"]
        
        # Code & Scripts
        if ext in [".py", ".js", ".ts", ".html", ".css", ".cpp", ".c", ".rs", ".go", ".sh"]:
            category = "Code"
            tags = ["development", ext.lstrip(".")]
        # Financial & Invoices
        elif any(k in base for k in ["invoice", "receipt", "statement", "tax", "billing", "bill"]) or ext in [".csv", ".tsv"]:
            category = "Finance"
            tags = ["financial", "records"]
        # Media & Design
        elif ext in [".png", ".jpg", ".jpeg", ".svg", ".gif", ".webp", ".mp4", ".mov", ".mp3", ".wav"]:
            category = "Media"
            tags = ["media", "asset"]
        # Archives & Backups
        elif ext in [".zip", ".tar", ".gz", ".7z", ".rar", ".pkg", ".dmg"]:
            category = "Archives"
            tags = ["archive", "backup"]
        # Notes & Documentation
        elif ext in [".md", ".txt", ".rst"] or "note" in base or "todo" in base:
            category = "Notes"
            tags = ["notes", "text"]

        # Clean, human-readable name suggestion
        clean_stem = re.sub(r"[_\-\s]+", "_", base).strip("_")
        clean_name = f"{clean_stem}{ext}"

        return {
            "category": category,
            "suggested_name": clean_name,
            "tags": tags
        }

    def summarize_batch(self, file_infos: list) -> str:
        """Generate a concise, sloth-friendly change summary."""
        count = len(file_infos)
        if count == 0:
            return "No changes detected. Pure sloth bliss — nothing to do!"

        categories = {}
        for f in file_infos:
            cat = f.get("category", "General")
            categories[cat] = categories.get(cat, 0) + 1

        cat_summary = ", ".join([f"{v} {k}" for k, v in categories.items()])

        if self.use_gemma:
            prompt = (
                f"You are SlothSync AI, rewarding laziness. Summarize this sync batch in 2 cheerful, relaxed sentences: "
                f"{count} files modified/added across: {cat_summary}."
            )
            gemma_summary = self.query_gemma(prompt)
            if gemma_summary:
                return gemma_summary

        # Default high-quality summary
        return (
            f"SlothSync handled {count} file{'s' if count != 1 else ''} ({cat_summary}) quietly in the background. "
            f"Everything is safely organized and backed up without you lifting a finger."
        )
