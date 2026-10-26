#!/usr/bin/env python3
"""
Automated File Organizer and Cleanup Utility
Python Programming Internship - Task 3

Organizes files in a target directory into category subfolders
based on file extensions. Handles naming collisions and permission errors.
"""

import os
import shutil
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime


# ---------------------------------------------------------------------------
# Extension → Category mapping
# ---------------------------------------------------------------------------
EXTENSION_MAP = {
    # Documents
    ".pdf": "Documents",
    ".doc": "Documents",
    ".docx": "Documents",
    ".txt": "Documents",
    ".rtf": "Documents",
    ".odt": "Documents",
    ".xls": "Documents",
    ".xlsx": "Documents",
    ".ppt": "Documents",
    ".pptx": "Documents",
    ".csv": "Documents",
    ".md": "Documents",
    ".epub": "Documents",

    # Images
    ".jpg": "Images",
    ".jpeg": "Images",
    ".png": "Images",
    ".gif": "Images",
    ".bmp": "Images",
    ".svg": "Images",
    ".webp": "Images",
    ".ico": "Images",
    ".tiff": "Images",
    ".tif": "Images",
    ".heic": "Images",

    # Videos
    ".mp4": "Videos",
    ".mkv": "Videos",
    ".avi": "Videos",
    ".mov": "Videos",
    ".wmv": "Videos",
    ".flv": "Videos",
    ".webm": "Videos",
    ".m4v": "Videos",
    ".mpeg": "Videos",
    ".mpg": "Videos",

    # Audio
    ".mp3": "Audio",
    ".wav": "Audio",
    ".flac": "Audio",
    ".aac": "Audio",
    ".ogg": "Audio",
    ".m4a": "Audio",
    ".wma": "Audio",

    # Archives
    ".zip": "Archives",
    ".rar": "Archives",
    ".7z": "Archives",
    ".tar": "Archives",
    ".gz": "Archives",
    ".bz2": "Archives",
    ".xz": "Archives",
    ".tgz": "Archives",

    # Code / Development
    ".py": "Code",
    ".js": "Code",
    ".ts": "Code",
    ".java": "Code",
    ".c": "Code",
    ".cpp": "Code",
    ".h": "Code",
    ".hpp": "Code",
    ".cs": "Code",
    ".go": "Code",
    ".rs": "Code",
    ".rb": "Code",
    ".php": "Code",
    ".html": "Code",
    ".css": "Code",
    ".scss": "Code",
    ".json": "Code",
    ".xml": "Code",
    ".yaml": "Code",
    ".yml": "Code",
    ".sql": "Code",
    ".sh": "Code",
    ".bat": "Code",
    ".ps1": "Code",
    ".ipynb": "Code",

    # Executables / Installers
    ".exe": "Executables",
    ".msi": "Executables",
    ".dmg": "Executables",
    ".app": "Executables",
    ".deb": "Executables",
    ".rpm": "Executables",
    ".apk": "Executables",

    # Fonts
    ".ttf": "Fonts",
    ".otf": "Fonts",
    ".woff": "Fonts",
    ".woff2": "Fonts",
}

# Default category for unrecognized extensions
OTHER_CATEGORY = "Other"


def get_category(extension: str) -> str:
    """Return the target folder name for a given file extension."""
    return EXTENSION_MAP.get(extension.lower(), OTHER_CATEGORY)


def unique_destination(dest_dir: Path, filename: str) -> Path:
    """
    Resolve naming collisions by appending a counter.
    e.g. report.pdf → report (1).pdf → report (2).pdf
    """
    dest = dest_dir / filename
    if not dest.exists():
        return dest

    stem = Path(filename).stem
    suffix = Path(filename).suffix
    counter = 1
    while True:
        new_name = f"{stem} ({counter}){suffix}"
        dest = dest_dir / new_name
        if not dest.exists():
            return dest
        counter += 1


def organize_directory(target_dir: str | Path, dry_run: bool = False) -> dict:
    """
    Scan *target_dir* and move files into category subfolders.

    Returns a summary dictionary:
        {
            "moved": {category: [list of filenames], ...},
            "skipped": [(filename, reason), ...],
            "errors": [(filename, error_msg), ...],
        }
    """
    target = Path(target_dir).expanduser().resolve()

    if not target.is_dir():
        raise NotADirectoryError(f"'{target}' is not a valid directory.")

    summary = {
        "moved": defaultdict(list),
        "skipped": [],
        "errors": [],
    }

    # Use scandir for efficient directory iteration
    with os.scandir(target) as entries:
        for entry in entries:
            # Only process regular files sitting directly in the target folder
            if not entry.is_file(follow_symlinks=False):
                continue

            src_path = Path(entry.path)
            ext = src_path.suffix.lower()
            category = get_category(ext)
            dest_dir = target / category

            try:
                if dry_run:
                    # Simulate only
                    unique_dest = unique_destination(dest_dir, src_path.name)
                    summary["moved"][category].append(
                        f"{src_path.name} → {unique_dest.name}"
                    )
                    continue

                # Create category folder if needed
                dest_dir.mkdir(exist_ok=True)

                # Resolve potential name collision
                dest_path = unique_destination(dest_dir, src_path.name)

                # Perform the move
                shutil.move(str(src_path), str(dest_path))
                summary["moved"][category].append(
                    f"{src_path.name} → {dest_path.name}"
                    if dest_path.name != src_path.name
                    else src_path.name
                )

            except PermissionError:
                summary["errors"].append((src_path.name, "Permission denied"))
            except FileExistsError:
                # Extremely rare after unique_destination, but handle anyway
                summary["errors"].append((src_path.name, "Destination already exists"))
            except OSError as e:
                summary["errors"].append((src_path.name, str(e)))

    return summary


def print_summary(summary: dict, target: Path, dry_run: bool = False):
    """Pretty-print the organization results."""
    mode = "DRY-RUN (no files were moved)" if dry_run else "COMPLETED"
    print("\n" + "=" * 60)
    print(f"  FILE ORGANIZER — {mode}")
    print(f"  Target : {target}")
    print(f"  Time   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    total_moved = 0
    if summary["moved"]:
        print("\n📦 Files organized by category:\n")
        for category in sorted(summary["moved"].keys()):
            files = summary["moved"][category]
            total_moved += len(files)
            print(f"  [{category}] — {len(files)} file(s)")
            for name in files[:8]:          # show first few
                print(f"      • {name}")
            if len(files) > 8:
                print(f"      … and {len(files) - 8} more")
            print()
    else:
        print("\n  No files needed organizing.\n")

    if summary["skipped"]:
        print("⏭  Skipped:")
        for name, reason in summary["skipped"]:
            print(f"      • {name} ({reason})")
        print()

    if summary["errors"]:
        print("❌ Errors:")
        for name, err in summary["errors"]:
            print(f"      • {name}: {err}")
        print()

    print("-" * 60)
    print(f"  Total files relocated : {total_moved}")
    print(f"  Errors                : {len(summary['errors'])}")
    print("=" * 60)


def main():
    print("=" * 60)
    print("   AUTOMATED FILE ORGANIZER & CLEANUP UTILITY")
    print("=" * 60)

    # --- Get target directory ---
    if len(sys.argv) > 1:
        target_input = sys.argv[1]
    else:
        default = str(Path.home() / "Downloads")
        print(f"\nDefault target: {default}")
        target_input = input("Enter directory path to organize (or press Enter for default): ").strip()
        if not target_input:
            target_input = default

    target = Path(target_input).expanduser()

    if not target.exists():
        print(f"Error: Directory '{target}' does not exist.")
        sys.exit(1)
    if not target.is_dir():
        print(f"Error: '{target}' is not a directory.")
        sys.exit(1)

    # --- Dry-run option ---
    dry = False
    if len(sys.argv) > 2 and sys.argv[2] in ("--dry-run", "-n"):
        dry = True
    else:
        ans = input("\nPerform a dry-run first (preview only)? [Y/n]: ").strip().lower()
        dry = ans not in ("n", "no")

    if dry:
        print("\n🔍 Running in DRY-RUN mode (no files will be moved)…")
        summary = organize_directory(target, dry_run=True)
        print_summary(summary, target.resolve(), dry_run=True)

        proceed = input("\nProceed with actual file moves? [y/N]: ").strip().lower()
        if proceed not in ("y", "yes"):
            print("Aborted. No files were moved.")
            return

    # --- Real run ---
    print("\n🚀 Organizing files…")
    summary = organize_directory(target, dry_run=False)
    print_summary(summary, target.resolve(), dry_run=False)


if __name__ == "__main__":
    main()
