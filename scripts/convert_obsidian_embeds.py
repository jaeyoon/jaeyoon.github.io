#!/usr/bin/env python3

from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys
from typing import Iterable


IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".svg",
    ".avif",
}

EMBED_PATTERN = re.compile(r"!\[\[([^\]]+)\]\]")


def repo_root() -> pathlib.Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        check=True,
        capture_output=True,
        text=True,
    )
    return pathlib.Path(result.stdout.strip())


def staged_markdown_files(root: pathlib.Path) -> list[pathlib.Path]:
    result = subprocess.run(
        [
            "git",
            "diff",
            "--cached",
            "--name-only",
            "-z",
            "--diff-filter=ACM",
            "--",
            "*.md",
        ],
        check=True,
        capture_output=True,
    )
    paths = [p for p in result.stdout.decode("utf-8").split("\x00") if p]
    return [root / path for path in paths]


def dedupe(paths: Iterable[pathlib.Path]) -> list[pathlib.Path]:
    unique: list[pathlib.Path] = []
    seen: set[pathlib.Path] = set()
    for path in paths:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique.append(path)
    return unique


def is_inside_repo(root: pathlib.Path, path: pathlib.Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def candidate_paths(root: pathlib.Path, note_path: pathlib.Path, target: str) -> list[pathlib.Path]:
    note_dir = note_path.parent
    normalized = target.strip().lstrip("/")
    relative_target = pathlib.PurePosixPath(normalized)
    candidates: list[pathlib.Path] = []

    if len(relative_target.parts) > 1:
        candidates.extend([note_dir / relative_target, root / relative_target])
    else:
        basename = normalized
        candidates.extend(
            [
                note_dir / basename,
                note_dir / "assets" / basename,
                root / basename,
                root / "assets" / basename,
            ]
        )
        candidates.extend(sorted(root.rglob(basename)))

    return [
        candidate
        for candidate in dedupe(candidates)
        if candidate.exists() and candidate.is_file() and is_inside_repo(root, candidate)
    ]


def resolve_embed(root: pathlib.Path, note_path: pathlib.Path, raw_embed: str) -> pathlib.Path | None:
    target = raw_embed.split("|", 1)[0].strip()
    for candidate in candidate_paths(root, note_path, target):
        if candidate.suffix.lower() in IMAGE_EXTENSIONS:
            return candidate
    return None


def alt_text(raw_embed: str, image_path: pathlib.Path) -> str:
    parts = raw_embed.split("|", 1)
    if len(parts) == 2:
        alias = parts[1].strip()
        if alias and not re.fullmatch(r"\d+(x\d+)?", alias):
            return alias
    text = image_path.stem.replace("_", " ").replace("-", " ")
    return re.sub(r"\s+", " ", text).strip()


def convert_embeds(root: pathlib.Path, note_path: pathlib.Path, text: str) -> tuple[str, bool]:
    changed = False

    def replace(match: re.Match[str]) -> str:
        nonlocal changed
        raw_embed = match.group(1).strip()
        image_path = resolve_embed(root, note_path, raw_embed)
        if image_path is None:
            return match.group(0)
        changed = True
        relative = image_path.resolve().relative_to(root.resolve()).as_posix()
        return f"![{alt_text(raw_embed, image_path)}](</{relative}>)"

    return EMBED_PATTERN.sub(replace, text), changed


def process_file(root: pathlib.Path, note_path: pathlib.Path) -> bool:
    if not note_path.exists() or note_path.suffix.lower() != ".md":
        return False
    original = note_path.read_text(encoding="utf-8")
    updated, changed = convert_embeds(root, note_path, original)
    if not changed or updated == original:
        return False
    note_path.write_text(updated, encoding="utf-8")
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert Obsidian image embeds into web-compatible Markdown image links."
    )
    parser.add_argument("files", nargs="*", help="Markdown files to process")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = repo_root()
    files = [root / path for path in args.files] if args.files else staged_markdown_files(root)
    changed_files = [path for path in files if process_file(root, path)]
    for path in changed_files:
        print(path.relative_to(root).as_posix())
    return 0


if __name__ == "__main__":
    sys.exit(main())
