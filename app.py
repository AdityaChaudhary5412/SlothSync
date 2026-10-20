"""
SlothSync - Web Application & REST API
Zero-dependency Python 3 native HTTP server powering the SlothSync dashboard.
"""

import json
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from sync_engine import SlothSyncEngine

BASE_DIR = Path(__file__).parent.resolve()
STATIC_DIR = BASE_DIR / "static"


class SlothSyncRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def _send_json(self, data: dict, status: int = 200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/status":
            engine = SlothSyncEngine(str(BASE_DIR / "samples" / "messy_files"), str(BASE_DIR / "samples" / "backup"))
            manifests = [f.name for f in sorted(list(engine.manifest_dir.glob("*.json")), reverse=True)]
            self._send_json({
                "status": "ready",
                "ai_engine": "Gemma 2B (Local)" if engine.ai.use_gemma else "Deterministic Heuristics (Offline)",
                "use_gemma": engine.ai.use_gemma,
                "manifest_count": len(manifests),
                "recent_manifests": manifests[:5]
            })
            return

        if self.path == "/api/logs":
            engine = SlothSyncEngine(str(BASE_DIR / "samples" / "messy_files"), str(BASE_DIR / "samples" / "backup"))
            logs = []
            for lf in sorted(list(engine.logs_dir.glob("*.md")), reverse=True)[:5]:
                try:
                    logs.append({"name": lf.name, "content": lf.read_text(encoding="utf-8")})
                except Exception:
                    pass
            self._send_json({"logs": logs})
            return

        # Serve static files
        super().do_GET()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(length) if length > 0 else b"{}"
        try:
            params = json.loads(post_data.decode("utf-8"))
        except Exception:
            params = {}

        source = params.get("source", str(BASE_DIR / "samples" / "messy_files"))
        backup = params.get("backup", str(BASE_DIR / "samples" / "backup"))
        engine = SlothSyncEngine(source, backup)

        if self.path == "/api/scan":
            result = engine.scan()
            self._send_json(result)
            return

        if self.path == "/api/sync":
            organize = params.get("organize", True)
            result = engine.execute_sync(organize_by_category=organize)
            self._send_json(result)
            return

        if self.path == "/api/rollback":
            result = engine.rollback_last_sync()
            self._send_json(result)
            return

        self._send_json({"error": "Endpoint not found"}, status=404)


def run_server(port=8765):
    server_address = ("", port)
    httpd = HTTPServer(server_address, SlothSyncRequestHandler)
    print(f"🦥 SlothSync Dashboard active at http://localhost:{port}")
    print("Press Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nSloth is resting. Server stopped.")
        httpd.server_close()


if __name__ == "__main__":
    p = 8765
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        p = int(sys.argv[1])
    run_server(p)
