#!/usr/bin/env python3
"""
CosDenOS Repository Structure Validator
---------------------------------------

Run manually:

    python tools/validate_cosden_structure.py

Or set as a CI check in GitHub Actions.

This script validates:

- Required directories exist
- Required files exist
- No files exist in invalid locations
- Known module paths are correctly structured
- CosDenOS imports resolve cleanly
"""

import os
import sys
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# --------------------------
# CONFIGURATION: EXPECTED TREE
# --------------------------

REQUIRED_DIRS = {
    "src",
    "src/CosDenOS",
    "src/CosDenOS/clients",
    ".github",
    ".github/workflows",
}

REQUIRED_FILES = {
    "pyproject.toml",
    "Dockerfile",
    "src/CosDenOS/api.py",
    "src/CosDenOS/api_models.py",
    "src/CosDenOS/logging_utils.py",
    "src/CosDenOS/stegcore_integration.py",
    "src/CosDenOS/user_profile.py",
    "src/CosDenOS/ai_planner.py",
    "src/CosDenOS/clients/python_client.py",
    "src/CosDenOS/clients/__init__.py",
    ".github/workflows/cosden-docker.yml",
}

ALLOWED_EXTRA_DIRS = {
    "engine",
    "tests",
    "examples",
    "docs",
    "data",
}


# --------------------------
# Console helpers
# --------------------------

def green(msg): return f"\033[92m{msg}\033[0m"
def yellow(msg): return f"\033[93m{msg}\033[0m"
def red(msg): return f"\033[91m{msg}\033[0m"


# --------------------------
# Validator functions
# --------------------------

def check_required_dirs():
    errs = []
    for d in REQUIRED_DIRS:
        if not (ROOT / d).exists():
            errs.append(f"Missing directory: {d}")
    return errs


def check_required_files():
    errs = []
    for f in REQUIRED_FILES:
        if not (ROOT / f).exists():
            errs.append(f"Missing file: {f}")
    return errs


def find_unexpected_structure():
    """Scan repo for unknown top-level entries and misplaced files."""
    errs = []

    # Allowed top-level entries
    allowed_root = {
        "src", ".github", "tools", "README.md", "pyproject.toml", "Dockerfile",
        ".gitignore", "LICENSE"
    }

    for item in ROOT.iterdir():
        if item.is_dir() and item.name not in allowed_root:
            errs.append(f"Unknown directory at root: {item.name}")
        if item.is_file() and item.name not in allowed_root:
            errs.append(f"Unexpected file at root: {item.name}")

    # Scan src/CosDenOS for misplaced files
    cosden_root = ROOT / "src" / "CosDenOS"
    if cosden_root.exists():
        for item in cosden_root.iterdir():
            if item.is_dir() and item.name not in ["clients", "engine"] and item.name not in ALLOWED_EXTRA_DIRS:
                errs.append(f"Unexpected folder inside CosDenOS/: {item.name}")

    return errs


def try_import_cosden():
    """
    Ensure CosDenOS can be imported cleanly.
    """
    errs = []
    cosden_path = ROOT / "src" / "CosDenOS"
    if not cosden_path.exists():
        return ["CosDenOS directory missing — cannot validate imports"]

    spec = importlib.util.spec_from_file_location("CosDenOS", cosden_path / "__init__.py")
    if spec is None:
        return ["Failed to construct import spec for CosDenOS"]

    try:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore
    except Exception as exc:
        errs.append(f"CosDenOS import failed: {exc}")

    return errs


# --------------------------
# Main Execution
# --------------------------

def main():
    print("\n🔍 Validating CosDenOS repo structure...\n")

    errors = []
    checks = [
        ("Required directories", check_required_dirs),
        ("Required files", check_required_files),
        ("Unexpected structure", find_unexpected_structure),
        ("Import check", try_import_cosden),
    ]

    for title, fn in checks:
        print(f"• {title}...")
        result = fn()
        if result:
            for r in result:
                print("   " + red("✗ " + r))
            errors.extend(result)
        else:
            print("   " + green("✓ OK"))

    print("\n-----------------------------------")
    if errors:
        print(red("❌ Validation failed"))
        print("Fix the above issues before committing.")
        sys.exit(1)
    else:
        print(green("✅ Validation passed — repo structure is correct!"))
        sys.exit(0)


if __name__ == "__main__":
    main()
