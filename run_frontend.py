"""
Equiderma AI - Frontend Launcher
Launches the Streamlit Clinical Advisor Dashboard.
"""

import sys
import os
from pathlib import Path
from streamlit.web import cli as stcli

if __name__ == "__main__":
    dashboard_path = str(Path(__file__).resolve().parent / "frontend" / "dashboard.py")
    sys.argv = ["streamlit", "run", dashboard_path, "--server.port=8501", "--browser.gatherUsageStats=false"]
    sys.exit(stcli.main())
