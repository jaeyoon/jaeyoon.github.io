#!/usr/bin/env python3

from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys


INDEX_PATH = pathlib.Path("index.md")


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


def parse_front_matter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    lines = text.splitlines()
    try:
        closing_index = lines.index("---", 1)
    except ValueError:
        return {}

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
    return data


def build_entry(title: str, permalink: str) -> str:
    return f"- [{title}]({permalink})"


def local_markdown_target(relative_file: str) -> str:
    path = pathlib.PurePosixPath(relative_file)
    without_suffix = path.with_suffix("").as_posix()
    if " " in without_suffix:
        return f"<{without_suffix}>"
    return without_suffix


def build_best_effort_entry(relative_file: str, title: str, permalink: str) -> str:
    relative_without_suffix = pathlib.PurePosixPath(relative_file).with_suffix("").as_posix()
    permalink_path = permalink.strip("/")
    local_target = local_markdown_target(relative_file)

    # If note path and web route align, use one link that works in both places.
    if relative_without_suffix == permalink_path:
        return f"- [{title}]({relative_without_suffix})"

    # Otherwise prefer a local Obsidian link and keep an explicit web link.
    return f"- [{title}]({local_target}) ([web]({permalink}))"


def insert_into_notes_section(index_text: str, entry: str, permalink: str, title: str) -> tuple[str, bool]:
    lines = index_text.splitlines()

    if any(f"]({permalink})" in line or f"- [{title}]" in line for line in lines):
        return index_text, False

    notes_heading_index = None
    for i, line in enumerate(lines):
        if line.strip() == "## Notes":
            notes_heading_index = i
            break

    if notes_heading_index is None:
        raise ValueError("Could not find '## Notes' section in index.md.")

    insert_at = notes_heading_index + 1
    while insert_at < len(lines):
        stripped = lines[insert_at].strip()
        if not stripped or stripped.startswith("- "):
            insert_at += 1
            continue
        break

    updated_lines = lines[:insert_at] + [entry] + lines[insert_at:]
    updated_text = "\n".join(updated_lines)
    if index_text.endswith("\n"):
        updated_text += "\n"
    return updated_text, True


def process_file(root: pathlib.Path, relative_file: str) -> tuple[bool, str]:
    note_path = (root / relative_file).resolve()
    index_path = (root / INDEX_PATH).resolve()

    if not note_path.exists():
        raise FileNotFoundError(relative_file)
    if not is_inside_repo(root, note_path):
        raise ValueError("Path is outside the repository.")
    if note_path.suffix.lower() != ".md":
        raise ValueError("Only Markdown files are supported.")
    if not index_path.exists():
        raise FileNotFoundError("index.md")

    front_matter = parse_front_matter(note_path.read_text(encoding="utf-8"))
    title = front_matter.get("title")
    permalink = front_matter.get("permalink")

    if not title or not permalink:
        raise ValueError("Current note must have front matter with both title and permalink.")

    index_text = index_path.read_text(encoding="utf-8")
    entry = build_best_effort_entry(relative_file, title, permalink)
    updated, changed = insert_into_notes_section(index_text, entry, permalink, title)
    if not changed:
        return False, entry

    index_path.write_text(updated, encoding="utf-8")
    return True, entry


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Append the current note's title/permalink to the Notes section in index.md."
    )
    parser.add_argument("file", help="Markdown file path relative to the repository root")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = repo_root()

    try:
        changed, entry = process_file(root, args.file)
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if changed:
        print(f"Added to index.md: {entry}")
    else:
        print(f"Entry already exists in index.md: {entry}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
