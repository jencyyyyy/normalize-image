import sys
import os

# Make the project root (one level up) importable so "from app import app" works
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import app  # noqa: E402

# Vercel's Python runtime looks for a WSGI-compatible object named "app"
# in this module.
