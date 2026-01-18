#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["beautifulsoup4", "lxml"]
# ///
"""
HTML Validator for Agentic Finance Review

Validates the generated index.html dashboard files:
- Valid HTML structure (html, head, body, title tags)
- At least 5 images present (graphs from assets/)
- All referenced image files exist

Outputs JSON decision for Claude Code Stop hook:
- {"decision": "block", "reason": "..."} to block and retry
- {} to allow completion
"""
import json
import sys
from pathlib import Path
from datetime import datetime

from bs4 import BeautifulSoup

# Default operations directory - used when no argument provided
ROOT_OPERATIONS_DIR = Path("apps/agentic-finance-review/data/mock_dataset_2026")

# Log file in same directory as this script
LOG_FILE = Path(__file__).parent / "html-validator.log"

MIN_IMAGES = 5


def log(message: str):
    """Append timestamped message to log file."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")


def validate_html(file_path: Path) -> list[str]:
    """Validate an HTML file. Returns list of error messages."""
    errors = []

    if not file_path.exists():
        log(f"  ✗ File not found: {file_path}")
        return [f"File not found: {file_path}"]

    try:
        content = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        log(f"  ✗ Encoding error: {e}")
        return [f"Encoding error in {file_path}: {e}"]

    if not content.strip():
        log("  ✗ HTML file is empty")
        return [f"{file_path.name}: HTML file is empty"]

    # Parse HTML
    try:
        soup = BeautifulSoup(content, "lxml")
    except Exception as e:
        log(f"  ✗ Failed to parse HTML: {e}")
        return [f"Failed to parse HTML {file_path}: {e}"]

    # Check for basic HTML structure
    if soup.find("html"):
        log("  ✓ <html> tag")
    else:
        log("  ✗ Missing <html> tag")
        errors.append(f"{file_path.name}: Missing <html> tag")

    if soup.find("head"):
        log("  ✓ <head> tag")
    else:
        log("  ✗ Missing <head> tag")
        errors.append(f"{file_path.name}: Missing <head> tag")

    if soup.find("body"):
        log("  ✓ <body> tag")
    else:
        log("  ✗ Missing <body> tag")
        errors.append(f"{file_path.name}: Missing <body> tag")

    if soup.find("title"):
        log("  ✓ <title> tag")
    else:
        log("  ✗ Missing <title> tag")
        errors.append(f"{file_path.name}: Missing <title> tag")

    # Check for images and verify they exist
    parent_dir = file_path.parent
    images = soup.find_all("img")
    valid_images = 0

    log(f"  Checking {len(images)} images...")
    for img in images:
        src = img.get("src", "")
        if not src:
            continue

        # Handle relative paths - verify image exists
        if not src.startswith(("http://", "https://", "data:")):
            img_path = parent_dir / src
            if img_path.exists():
                valid_images += 1
                log(f"    ✓ {src}")
            else:
                log(f"    ✗ {src} (not found)")
                errors.append(f"{file_path.name}: Referenced image not found: {src}")
        else:
            # External/data URLs count as valid
            valid_images += 1
            log(f"    ✓ {src[:50]}... (external)")

    # Require at least MIN_IMAGES images
    if valid_images < MIN_IMAGES:
        log(f"  ✗ Found {valid_images} images, expected at least {MIN_IMAGES}")
        errors.append(f"{file_path.name}: Found {valid_images} images, expected at least {MIN_IMAGES}")
    else:
        log(f"  ✓ {valid_images} valid images (min: {MIN_IMAGES})")

    return errors


def validate_directory(dir_path: Path) -> list[str]:
    """Validate index.html in a directory."""
    if not dir_path.exists():
        log(f"  ✗ Directory not found: {dir_path}")
        return [f"Directory not found: {dir_path}"]

    index_file = dir_path / "index.html"
    if not index_file.exists():
        log(f"  ✗ index.html not found in {dir_path}")
        return [f"index.html not found in {dir_path}"]

    log(f"  Validating: {index_file}")
    return validate_html(index_file)


def main():
    log("=" * 50)
    log("HTML VALIDATOR STOP HOOK TRIGGERED")

    # Read hook input from stdin (Claude Code passes JSON)
    # Currently unused but kept for future extensibility
    try:
        stdin_data = sys.stdin.read()
        if stdin_data.strip():
            _hook_input = json.loads(stdin_data)
        else:
            _hook_input = {}
    except json.JSONDecodeError:
        _hook_input = {}

    # Get target from command line arg, default to ROOT_OPERATIONS_DIR
    if len(sys.argv) > 1:
        target = Path(sys.argv[1])
        log(f"Target (from arg): {target}")
    else:
        target = ROOT_OPERATIONS_DIR
        log(f"Target (default): {target}")

    # Validate based on target type
    if target.is_file() and target.suffix == ".html":
        log(f"Validating single file: {target.name}")
        errors = validate_html(target)
    elif target.is_dir():
        log(f"Validating directory: {target}")
        errors = validate_directory(target)
    else:
        errors = [f"Target is not an HTML file or directory: {target}"]
        log(f"✗ Invalid target: {target}")

    # Output decision JSON
    if errors:
        log(f"RESULT: BLOCK ({len(errors)} errors)")
        for err in errors:
            log(f"  ✗ {err}")
        print(json.dumps({
            "decision": "block",
            "reason": "HTML validation failed:\n" + "\n".join(errors)
        }))
    else:
        log("RESULT: PASS - HTML validation successful")
        print(json.dumps({}))

if __name__ == "__main__":
    main()
