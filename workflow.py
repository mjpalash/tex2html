#!/usr/bin/env python3
"""
texpub_workflow.py

Single entry point to run the full LaTeX → HTML → GitHub Pages workflow.

Assumed scripts in the *same directory* as this file:

  - setup_texpub.py      (Script A: create settings/config)
  - convert_texpub.py    (Script B: pandoc + copy into Sites repo)
  - buildindex_texpub.py (Script C: rebuild index listing articles)
  - gitpush_texpub.py    (Script D: git add/commit/push if settings allow)

Workflow:
1. Ensure texpub.cfg (or settings) exists; if not, run setup script.
2. Run convert script.
3. Run buildindex script.
4. Run gitpush script (it will decide, based on settings, whether to actually push).

How this orchestrator behaves:
Checks for texpub.cfg (or whatever settings file you are using) in the
current directory. If missing, it asks to run setup_texpub.py. After
setup, it expects the file to be present. Then it runs Script B
(convert_texpub.py), which performs the pandoc conversion and copies
index.html plus images into a new article folder inside the Sites repo.
Next it runs Script C (buildindex_texpub.py), which regenerates the
index page listing the available article folders. Finally it runs Script
D (gitpush_texpub.py), which reads the settings (for example, push_mode)
and decides whether to push the changes to GitHub or exit without
pushing. Adjust the filenames (SETUP_SCRIPT, CONVERT_SCRIPT, etc.) to
match the actual names used in your environment.

"""

import configparser
import subprocess
import sys
from pathlib import Path
from typing import Optional

CONFIG_FILENAME = "texpub.cfg"

SCRIPT_DIR = Path(__file__).resolve().parent

# You can rename these if your file names differ.
SETUP_SCRIPT      = SCRIPT_DIR / "setup.py"
CONVERT_SCRIPT    = SCRIPT_DIR / "convert.py"
BUILDINDEX_SCRIPT = SCRIPT_DIR / "buildindex.py"
GITPUSH_SCRIPT    = SCRIPT_DIR / "gitpush.py"


def run_python_script(script_path: Path) -> int:
    """Run another Python script via subprocess, return its exit code."""
    try:
        completed = subprocess.run(
            [sys.executable, str(script_path)],
            check=False,
        )
        return completed.returncode
    except FileNotFoundError:
        print(f"Error: Could not run script {script_path}")
        return 1


def prompt_yes_no(message: str, default: Optional[bool] = None) -> bool:
    while True:
        if default is True:
            prompt = " (y/n) [y]: "
        elif default is False:
            prompt = " (y/n) [n]: "
        else:
            prompt = " (y/n): "

        ans = input(message + prompt).strip().lower()

        if ans == "" and default is not None:
            return default
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False

        print("Please enter 'y' or 'n'.")


def ensure_config() -> Path:
    """
    Ensure the main settings file exists in the current working directory.

    If not, and if setup script is available, offer to run setup.
    """
    config_path = Path.cwd() / CONFIG_FILENAME
    if config_path.is_file():
        return config_path

    print(f"Settings file '{CONFIG_FILENAME}' not found in {Path.cwd()}.")

    if not SETUP_SCRIPT.is_file():
        print(f"Setup script not found at {SETUP_SCRIPT}. Cannot create settings.")
        sys.exit(1)

    if prompt_yes_no("Run setup script now to create it?", default=True):
        code = run_python_script(SETUP_SCRIPT)
        if code != 0:
            print("Setup script failed. Cannot continue.")
            sys.exit(code)

        if not config_path.is_file():
            print("Settings file still not found after running setup. Aborting.")
            sys.exit(1)

        return config_path
    else:
        print("Aborting. Please run the setup script manually.")
        sys.exit(0)


def main() -> int:
    print("=== texpub workflow (setup → convert → buildindex → gitpush) ===")

    # 1. Ensure settings exist (Script A)
    config_path = ensure_config()
    print(f"\nUsing settings file: {config_path}")

    # (Optional: just show where Sites repo is, if you want a quick sanity check)
    cfg = configparser.ConfigParser()
    cfg.read(config_path)
    if "github" in cfg and "repo_path" in cfg["github"]:
        print(f"Sites repo: {cfg['github']['repo_path']}")
    else:
        print("Warning: [github].repo_path not found in settings (setup script should define this).")

    # 2. Run convert script (Script B)
    if not CONVERT_SCRIPT.is_file():
        print(f"\nError: convert script not found at {CONVERT_SCRIPT}")
        return 1

    print("\n--- Step 1: Convert LaTeX to HTML and copy to Sites repo (Script B) ---")
    code = run_python_script(CONVERT_SCRIPT)
    if code != 0:
        print(f"convert_texpub.py exited with code {code}. Aborting workflow.")
        return code

    # 3. Run buildindex script (Script C)
    if not BUILDINDEX_SCRIPT.is_file():
        print(f"\nError: buildindex script not found at {BUILDINDEX_SCRIPT}")
        return 1

    print("\n--- Step 2: Rebuild index listing articles (Script C) ---")
    code = run_python_script(BUILDINDEX_SCRIPT)
    if code != 0:
        print(f"buildindex_texpub.py exited with code {code}. Aborting workflow.")
        return code

    # 4. Run gitpush script (Script D)
    if not GITPUSH_SCRIPT.is_file():
        print(f"\nGit push script not found at {GITPUSH_SCRIPT}. Skipping git step.")
        print("You can run git commands manually if needed.")
        return 0

    print("\n--- Step 3: Git add/commit/push if settings allow (Script D) ---")
    code = run_python_script(GITPUSH_SCRIPT)
    if code != 0:
        print(f"gitpush_texpub.py exited with code {code}.")
        return code

    print("\nWorkflow complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


