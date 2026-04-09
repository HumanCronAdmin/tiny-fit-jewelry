"""Pinterest full auto-pipeline.

Runs the complete flow:
  1. Generate diverse content pins (comparisons, seasonal, tips, etc.)
  2. Detect new site pages → generate pins + images
  3. Generate images for any pins missing them
  4. Validate all pending pins (link check, image check, etc.)
  5. Post validated pins to Pinterest via API

This is what Task Scheduler calls daily.

Usage:
  python pinterest_pipeline.py          # Full run
  python pinterest_pipeline.py --dry    # Preview only
"""
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PYTHON = sys.executable
LOG_FILE = SCRIPT_DIR / "pipeline_log.txt"


def log(msg):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    line = f"[{now}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def run_step(name, script, extra_args=None):
    """Run a pipeline step and return True if successful."""
    log(f"=== Step: {name} ===")
    cmd = [PYTHON, str(SCRIPT_DIR / script)]
    if extra_args:
        cmd.extend(extra_args)

    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")

    if result.stdout:
        for line in result.stdout.strip().split("\n"):
            log(f"  {line}")

    if result.returncode != 0:
        log(f"  [ERROR] Exit code {result.returncode}")
        if result.stderr:
            for line in result.stderr.strip().split("\n")[:5]:
                log(f"  STDERR: {line}")
        return False

    return True


def main():
    dry_run = "--dry" in sys.argv
    dry_args = ["--dry"] if dry_run else []

    log("=" * 50)
    log("Pinterest Pipeline START" + (" [DRY RUN]" if dry_run else ""))
    log("=" * 50)

    # Step 1: Generate diverse content pins from brands.json
    run_step("Generate content pins", "content_generator.py", dry_args)

    # Step 2: Detect new site pages → generate page-based pins + images
    run_step("Auto-generate page pins", "auto_generate_pins.py", dry_args)

    # Step 3: Generate images for any pins that need them
    run_step("Generate missing images", "generate_missing_images.py", dry_args)

    # Step 4: Validate all pending pins
    run_step("Validate pins", "validate_pins.py", ["--fix"])

    # Step 3: Post validated pins (skip in dry run)
    if dry_run:
        log("=== Step: Post pins [SKIPPED - dry run] ===")
    else:
        run_step("Post to Pinterest", "pinterest_scheduler.py", ["--limit", "5"])

    log("Pinterest Pipeline DONE")
    log("")


if __name__ == "__main__":
    main()
