#!/usr/bin/env python3

from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys


IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".svg",
    ".avif",
    ".bmp",
}
ASSET_EXTENSIONS = IMAGE_EXTENSIONS | {
    ".pdf",
    ".mp4",
    ".mov",
    ".webm",
}
EMBED_PATTERN = re.compile(r"!\[\[([^\]]+)\]\]")
MARKDOWN_LINK_PATTERN = re.compile(r"(!?\[[^\]]*\]\()<?([^)\n>]+)>?(\))")


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


def dedupe(paths: list[pathlib.Path]) -> list[pathlib.Path]:
    unique: list[pathlib.Path] = []
    seen: set[pathlib.Path] = set()
    for path in paths:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique.append(path)
    return unique


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
                root / "notes" / "assets" / basename,
            ]
        )

    return [
        candidate
        for candidate in dedupe(candidates)
        if candidate.exists() and candidate.is_file() and is_inside_repo(root, candidate)
    ]


def resolve_asset(root: pathlib.Path, note_path: pathlib.Path, target: str) -> pathlib.Path | None:
    raw_target = target.split("|", 1)[0].strip()
    for candidate in candidate_paths(root, note_path, raw_target):
        if candidate.suffix.lower() in ASSET_EXTENSIONS:
            return candidate
    return None


def alt_text(raw_embed: str, asset_path: pathlib.Path) -> str:
    parts = raw_embed.split("|", 1)
    if len(parts) == 2:
        alias = parts[1].strip()
        if alias and not re.fullmatch(r"\d+(x\d+)?", alias):
            return alias
    text = asset_path.stem.replace("_", " ").replace("-", " ")
    return re.sub(r"\s+", " ", text).strip()


def convert_obsidian_embeds(root: pathlib.Path, note_path: pathlib.Path, text: str) -> tuple[str, int]:
    replacements = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal replacements
        raw_embed = match.group(1).strip()
        asset_path = resolve_asset(root, note_path, raw_embed)
        if asset_path is None or asset_path.suffix.lower() not in IMAGE_EXTENSIONS:
            return match.group(0)
        replacements += 1
        relative = asset_path.resolve().relative_to(root.resolve()).as_posix()
        return f"![{alt_text(raw_embed, asset_path)}](</{relative}>)"

    return EMBED_PATTERN.sub(replace, text), replacements


def convert_markdown_asset_links(root: pathlib.Path, note_path: pathlib.Path, text: str) -> tuple[str, int]:
    replacements = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal replacements
        prefix, target, suffix = match.groups()
        stripped = target.strip()
        lowered = stripped.lower()

        if (
            lowered.startswith(("http://", "https://", "mailto:", "#", "/"))
            or stripped.startswith("{{")
        ):
            return match.group(0)

        asset_path = resolve_asset(root, note_path, stripped)
        if asset_path is None:
            return match.group(0)

        replacements += 1
        relative = asset_path.resolve().relative_to(root.resolve()).as_posix()
        return f"{prefix}</{relative}>{suffix}"

    return MARKDOWN_LINK_PATTERN.sub(replace, text), replacements


def process_file(root: pathlib.Path, relative_path: str) -> tuple[bool, int]:
    note_path = (root / relative_path).resolve()
    if not note_path.exists():
        raise FileNotFoundError(relative_path)
    if not is_inside_repo(root, note_path):
        raise ValueError("Path is outside the repository.")
    if note_path.suffix.lower() != ".md":
        raise ValueError("Only Markdown files are supported.")

    original = note_path.read_text(encoding="utf-8")
    updated, embed_count = convert_obsidian_embeds(root, note_path, original)
    updated, link_count = convert_markdown_asset_links(root, note_path, updated)
    total = embed_count + link_count

    if updated == original:
        return False, 0

    note_path.write_text(updated, encoding="utf-8")
    return True, total


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalize asset/image links in a Markdown note for GitHub Pages."
    )
    parser.add_argument("file", help="Markdown file path relative to the repository root")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = repo_root()

    try:
        changed, total = process_file(root, args.file)
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if changed:
        print(f"Updated {args.file} ({total} asset link(s) normalized).")
    else:
        print(f"No asset links needed changes in {args.file}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
