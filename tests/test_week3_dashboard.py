"""Smoke tests for src/dashboard.py (Week 3 target)."""

from __future__ import annotations

import sys
from pathlib import Path

# Add src to sys.path if not present
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


def test_dashboard_imports():
    """Verify that the dashboard module can be imported without executing Streamlit rendering."""
    try:
        import dashboard
        assert hasattr(dashboard, "main")
        assert callable(dashboard.main)
    except Exception as e:
        assert False, f"Failed to import dashboard: {e}"
