"""Pytest configuration file."""

import sys
from pathlib import Path

# Add compcheck_api directory to Python path
compcheck_api_path = Path(__file__).parent.parent / "comcheck_api"
sys.path.insert(0, str(compcheck_api_path))
