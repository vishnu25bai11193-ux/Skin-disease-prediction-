"""
Equiderma AI - Application Entrypoint (Flask API)
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend.server import app
from backend.config import SERVER_HOST, SERVER_PORT, DEBUG

if __name__ == "__main__":
    print(f"🚀 Equiderma AI Application starting on http://{SERVER_HOST}:{SERVER_PORT}")
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=DEBUG)