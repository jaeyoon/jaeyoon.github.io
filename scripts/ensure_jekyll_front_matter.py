#!/usr/bin/env python3

from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys


FRONT_MATTER_BOUNDARY = "---"


def repo_root() -> pathlib.Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        check=True,
        capture_output=True,
        text=True,
    )
    return pathlib.Path(result.stdout.strip())


def is_inside_repo(root: pathlib.Path, path: pathlib.Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def slugify(text: str) -> str:
    text = text.strip()
    pieces: list[str] = []
    pending_hyphen = False

    for char in text:
        if char.isalnum():
            if pending_hyphen and pieces:
                pieces.append("-")
            pieces.append(char.lower())
            pending_hyphen = False
        else:
            pending_hyphen = True

    slug = "".join(pieces).strip("-")
    return slug or "note"


def build_permalink(relative_path: pathlib.Path) -> str:
    without_suffix = relative_path.with_suffix("")
    segments = [slugify(part) for part in without_suffix.parts]
    return "/" + "/".join(segments) + "/"


def front_matter_values(relative_path: pathlib.Path) -> dict[str, str]:
    title = relative_path.stem
    return {
        "layout": "page",
        "title": f'"{title}"',
        "permalink": build_permalink(relative_path),
    }


def has_front_matter(text: str) -> bool:
    return text.startswith(f"{FRONT_MATTER_BOUNDARY}\n") or text == FRONT_MATTER_BOUNDARY


def ensure_front_matter(text: str, values: dict[str, str]) -> tuple[str, list[str]]:
    changed_keys: list[str] = []

    if not has_front_matter(text):
        block = [
            FRONT_MATTER_BOUNDARY,
            *(f"{key}: {value}" for key, value in values.items()),
            FRONT_MATTER_BOUNDARY,
            "",
        ]
        return "\n".join(block) + text.lstrip("\n"), list(values.keys())

    lines = text.splitlines()
    try:
        closing_index = lines.index(FRONT_MATTER_BOUNDARY, 1)
    except ValueError:
        block = [
            FRONT_MATTER_BOUNDARY,
            *(f"{key}: {value}" for key, value in values.items()),
            FRONT_MATTER_BOUNDARY,
            "",
        ]
        return "\n".join(block) + text.lstrip("\n"), list(values.keys())

    existing_keys = set()
    key_pattern = re.compile(r"^([A-Za-z0-9_-]+)\s*:")
    for line in lines[1:closing_index]:
        match = key_pattern.match(line)
        if match:
            existing_keys.add(match.group(1))

    inserts = []
    for key, value in values.items():
        if key not in existing_keys:
            inserts.append(f"{key}: {value}")
            changed_keys.append(key)

    if not inserts:
        return text, []

    updated_lines = lines[:closing_index] + inserts + lines[closing_index:]
    updated_text = "\n".join(updated_lines)
    if text.endswith("\n"):
        updated_text += "\n"
    return updated_text, changed_keys


def process_file(root: pathlib.Path, relative_file: str) -> tuple[bool, list[str]]:
    path = (root / relative_file).resolve()
    if not path.exists():
        raise FileNotFoundError(relative_file)
    if not is_inside_repo(root, path):
        raise ValueError("Path is outside the repository.")
    if path.suffix.lower() != ".md":
        raise ValueError("Only Markdown files are supported.")

    relative_path = path.relative_to(root)
    original = path.read_text(encoding="utf-8")
    updated, changed_keys = ensure_front_matter(original, front_matter_values(relative_path))
    if not changed_keys:
        return False, []

    path.write_text(updated, encoding="utf-8")
    return True, changed_keys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ensure a Markdown note has Jekyll front matter for GitHub Pages."
    )
    parser.add_argument("file", help="Markdown file path relative to the repository root")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = repo_root()

    try:
        changed, changed_keys = process_file(root, args.file)
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if changed:
        print(f"Updated {args.file}: added {', '.join(changed_keys)}.")
    else:
        print(f"No front matter changes needed in {args.file}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
