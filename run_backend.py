"""
Equiderma AI - Backend Launcher
Starts the Flask REST API on http://127.0.0.1:9999
"""

import sys
from pathlib import Path

# Fix Windows console UTF-8 encoding
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend.server import app
from backend.config import SERVER_HOST, SERVER_PORT, DEBUG

if __name__ == "__main__":
    print("=" * 60)
    print(f"[+] Starting Equiderma AI Flask Backend")
    print(f"[+] Serving on: http://{SERVER_HOST}:{SERVER_PORT}")
    print(f"[+] Local Multimodal Vision (Ollama, NO OpenCV)")
    print(f"[+] ChromaDB RAG Knowledge Base Attached")
    print("=" * 60)
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=DEBUG)
