"""
Equiderma AI - Backend Server Entrypoint
Starts the Flask REST API with ChromaDB RAG, skin tone analysis, and multimodal clinical advisor.
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
    print("[+] Equiderma AI: Flask Clinical Backend Engine")
    print(f"[+] Server listening on http://{SERVER_HOST}:{SERVER_PORT}")
    print("[+] ChromaDB RAG: Armed with skin tone & disease knowledge")
    print("[+] Local Multimodal Vision Advisor: Enabled (NO OpenCV)")
    print("=" * 60)
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=DEBUG)
