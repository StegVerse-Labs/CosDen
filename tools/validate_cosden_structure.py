#!/usr/bin/env python3
"""
CosDenOS Repository Structure + Metadata Validator
--------------------------------------------------

Run manually:

    python tools/validate_cosden_structure.py

What it does:
- Validates required directories and files exist
- Flags unexpected entries
- Computes SHA-256 hashes of repo files
- Writes metadata to meta/files.jsonl for DB/analytics use
"""

import os
import sys
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]

# --------------------------
# CONFIGURATION
# --------------------------

REQUIRED_DIRS = {
    "src",
    "src/CosDenOS",
    "src/CosDenOS/clients",
    ".github",
    ".github/workflows",
    "tools",
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
    "tools/validate_cosden_structure.py",
}

ALLOWED_EXTRA_DIRS = {
    "engine",
    "tests",
    "examples",
    "docs",
    "data",
}

# Where to write file metadata
META_DIR = ROOT / "meta"
META_FILE = META_DIR / "files.jsonl"

# --------------------------
# Console helpers
# --------------------------

def green(msg): return f"\033[92m{msg}\033[0m"
def yellow(msg): return f"\033[93m{msg}\033[0m"
def red(msg): return f"\033[91m{msg}\033[0m"


# --------------------------
# Validators
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
    errs = []

    allowed_root = {
        "src", ".github", "tools", "README.md", "pyproject.toml",
        "Dockerfile", ".gitignore", "LICENSE", "meta",
    }

    for item in ROOT.iterdir():
        if item.is_dir() and item.name not in allowed_root:
            errs.append(f"Unknown directory at root: {item.name}")
        if item.is_file() and item.name not in allowed_root:
            errs.append(f"Unexpected file at root: {item.name}")

    cosden_root = ROOT / "src" / "CosDenOS"
    if cosden_root.exists():
        for item in cosden_root.iterdir():
            if item.is_dir() and item.name not in ["clients", "engine"] and item.name not in ALLOWED_EXTRA_DIRS:
                errs.append(f"Unexpected folder inside CosDenOS/: {item.name}")

    return errs


def try_import_cosden():
    errs = []
    cosden_path = ROOT / "src" / "CosDenOS"
    init_file = cosden_path / "__init__.py"
    if not cosden_path.exists():
        return ["CosDenOS directory missing — cannot validate imports"]
    if not init_file.exists():
        return ["CosDenOS/__init__.py missing — cannot import package"]

    spec = importlib.util.spec_from_file_location("CosDenOS", init_file)
    if spec is None:
        return ["Failed to construct import spec for CosDenOS"]

    try:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore
    except Exception as exc:
        errs.append(f"CosDenOS import failed: {exc}")

    return errs


# --------------------------
# Hashing + metadata
# --------------------------

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def build_file_metadata():
    """
    Walk src/ and tools/, hash files, and write metadata to meta/files.jsonl.
    """
    META_DIR.mkdir(exist_ok=True)
    if META_FILE.exists():
        META_FILE.unlink()

    now = datetime.now(timezone.utc).isoformat()
    repo_name = ROOT.name

    issues_index = build_issues_index()

    with META_FILE.open("w", encoding="utf-8") as out:
        for rel_root in ["src", "tools"]:
            base = ROOT / rel_root
            if not base.exists():
                continue
            for path in base.rglob("*"):
                if path.is_dir():
                    continue
                rel_path = path.relative_to(ROOT).as_posix()
                file_hash = sha256_file(path)
                size = path.stat().st_size

                meta = {
                    "repo": repo_name,
                    "path": rel_path,
                    "sha256": file_hash,
                    "size_bytes": size,
                    "timestamp": now,
                    "valid_location": True,
                    "issues": [],
                }

                if rel_path not in REQUIRED_FILES and not rel_path.startswith("src/CosDenOS") and not rel_path.startswith("tools/"):
                    meta["valid_location"] = False
                    meta["issues"].append("unexpected_location")

                extra_issues = issues_index.get(rel_path)
                if extra_issues:
                    meta["valid_location"] = False
                    meta["issues"].extend(extra_issues)

                out.write(json.dumps(meta) + "\n")


def build_issues_index():
    """
    Build a quick mapping of file -> [issues] based on the structure checks.
    For now, we only use it to tag unexpected files/directories at a coarse level.
    """
    index = {}
    # We could refine this to match exact paths; for now, we leave it simple.
    return index


# --------------------------
# Main Execution
# --------------------------

def main():
    print("\n🔍 Validating CosDenOS repo structure + generating metadata...\n")

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

    print("\n• File hashing & metadata...")
    build_file_metadata()
    print("   " + green(f"✓ Wrote metadata to {META_FILE.relative_to(ROOT)}"))

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
