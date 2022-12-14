"""Tests for oak-ai."""
import os
from pathlib import Path

ROOT = os.path.abspath(os.path.dirname(__file__))
INPUT_DIR = Path(ROOT) / "input"
CASES_DIR = INPUT_DIR / "cases"
INSTANCES_DIR = INPUT_DIR / "instances"
OUTPUT_DIR = Path(ROOT) / "output"
