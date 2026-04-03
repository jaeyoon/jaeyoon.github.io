#!/usr/bin/env python3

from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys


FRONT_MATTER_BOUNDARY = "---"
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


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


def parse_front_matter(text: str) -> tuple[dict[str, str], int | None]:
    if not text.startswith("---\n"):
        return {}, None
    lines = text.splitlines()
    try:
        closing_index = lines.index("---", 1)
    except ValueError:
        return {}, None

    data: dict[str, str] = {}
    pattern = re.compile(r"^([A-Za-z0-9_-]+):\s*(.*)$")
    for line in lines[1:closing_index]:
        match = pattern.match(line)
        if not match:
            continue
        key = match.group(1)
        value = match.group(2).strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        data[key] = value
    return data, closing_index


def ensure_front_matter(text: str, title: str, permalink: str) -> tuple[str, list[str]]:
    changes: list[str] = []
    front_matter, closing_index = parse_front_matter(text)

    desired = {
        "layout": "page",
        "title": f'"{title}"',
        "permalink": permalink,
    }

    if closing_index is None:
        block = [
            FRONT_MATTER_BOUNDARY,
            *(f"{key}: {value}" for key, value in desired.items()),
            FRONT_MATTER_BOUNDARY,
            "",
        ]
        return "\n".join(block) + text.lstrip("\n"), list(desired.keys())

    lines = text.splitlines()
    key_pattern = re.compile(r"^([A-Za-z0-9_-]+)\s*:")
    key_to_line: dict[str, int] = {}
    for idx, line in enumerate(lines[1:closing_index], start=1):
        match = key_pattern.match(line)
        if match:
            key_to_line[match.group(1)] = idx

    for key, value in desired.items():
        replacement = f"{key}: {value}"
        if key in key_to_line:
            line_index = key_to_line[key]
            if lines[line_index] != replacement:
                lines[line_index] = replacement
                changes.append(key)
        else:
            lines.insert(closing_index, replacement)
            closing_index += 1
            changes.append(key)

    updated = "\n".join(lines)
    if text.endswith("\n"):
        updated += "\n"
    return updated, changes


def current_display_title(path: pathlib.Path, text: str) -> str:
    front_matter, _ = parse_front_matter(text)
    if front_matter.get("title"):
        return front_matter["title"]
    return path.stem


def validate_slug(slug: str) -> str:
    slug = slug.strip().lower()
    if not SLUG_RE.fullmatch(slug):
        raise ValueError("Slug must use lowercase letters, numbers, and hyphens only.")
    return slug


def process_file(root: pathlib.Path, relative_file: str, slug: str) -> tuple[pathlib.Path, list[str]]:
    slug = validate_slug(slug)
    current_path = (root / relative_file).resolve()
    if not current_path.exists():
        raise FileNotFoundError(relative_file)
    if not is_inside_repo(root, current_path):
        raise ValueError("Path is outside the repository.")
    if current_path.suffix.lower() != ".md":
        raise ValueError("Only Markdown files are supported.")

    original = current_path.read_text(encoding="utf-8")
    title = current_display_title(current_path, original)
    new_path = current_path.with_name(f"{slug}.md")

    if new_path != current_path and new_path.exists():
        raise ValueError(f"Target file already exists: {new_path.relative_to(root)}")

    relative_new_path = new_path.relative_to(root)
    permalink = "/" + relative_new_path.with_suffix("").as_posix() + "/"
    updated, changes = ensure_front_matter(original, title, permalink)

    if new_path != current_path:
        current_path.rename(new_path)
        changes = ["file"] + changes

    new_path.write_text(updated, encoding="utf-8")
    return relative_new_path, changes


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rename the current note to a public slug and ensure Jekyll front matter."
    )
    parser.add_argument("file", help="Markdown file path relative to the repository root")
    parser.add_argument("slug", help="Public slug to use as filename and permalink")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = repo_root()
    try:
        relative_new_path, changes = process_file(root, args.file, args.slug)
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    changed_summary = ", ".join(changes) if changes else "no content changes"
    print(f"Prepared {relative_new_path.as_posix()} ({changed_summary}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
