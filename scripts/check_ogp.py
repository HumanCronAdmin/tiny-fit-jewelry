"""
TinyFit Jewelry OGP/Twitter Card checker.
Scans all HTML files and reports missing meta tags.
Usage: python scripts/check_ogp.py
"""
import os
import re
import sys

REQUIRED_TAGS = [
    "og:title",
    "og:description",
    "og:image",
    "og:url",
    "og:type",
    "twitter:card",
    "twitter:title",
    "twitter:description",
    "twitter:image",
]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def check_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    missing = [tag for tag in REQUIRED_TAGS if tag not in content]
    return missing


def main():
    issues = []
    for root, dirs, files in os.walk(BASE_DIR):
        for fname in files:
            if not fname.endswith(".html"):
                continue
            fpath = os.path.join(root, fname)
            rel = os.path.relpath(fpath, BASE_DIR)
            missing = check_file(fpath)
            if missing:
                issues.append((rel, missing))

    if not issues:
        print("All HTML files have complete OGP + Twitter Card tags.")
        sys.exit(0)

    print(f"Found {len(issues)} file(s) with missing tags:\n")
    for rel, missing in sorted(issues):
        print(f"  {rel}")
        for tag in missing:
            print(f"    - {tag}")
        print()
    sys.exit(1)


if __name__ == "__main__":
    main()
