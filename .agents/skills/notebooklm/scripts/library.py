#!/usr/bin/env python3
"""Maintain the NotebookLM skill's local notebook library."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any


DEFAULT_LIBRARY = Path(__file__).resolve().parents[1] / "data" / "library.json"
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
NOTEBOOK_URL_RE = re.compile(r"^https://notebooklm\.google\.com/notebook/[^/?#]+(?:[?#].*)?$")
REQUIRED_FIELDS = ("id", "name", "url", "description", "topics", "use_cases")
RESERVED_IDS = frozenset({"none"})


def canonicalize_notebook_url(value: Any) -> str:
    if not isinstance(value, str):
        raise LibraryError("url must be a string")
    stripped = value.strip()
    if not NOTEBOOK_URL_RE.match(stripped):
        raise LibraryError("url must be a NotebookLM URL")
    return re.sub(r"[?#].*$", "", stripped)


class LibraryError(Exception):
    pass


def load_library(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"notebooks": [], "active_notebook_id": None}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise LibraryError(f"invalid JSON: {exc}") from exc
    validate_library(data)
    return data


def write_library(path: Path, data: dict[str, Any]) -> None:
    validate_library(data)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    with NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as tmp:
        tmp.write(payload)
        tmp_path = Path(tmp.name)
    tmp_path.replace(path)


def validate_library(data: Any) -> None:
    if not isinstance(data, dict):
        raise LibraryError("library root must be an object")
    notebooks = data.get("notebooks")
    if not isinstance(notebooks, list):
        raise LibraryError("notebooks must be an array")
    active = data.get("active_notebook_id")
    if active is not None and not isinstance(active, str):
        raise LibraryError("active_notebook_id must be null or a string")

    seen: set[str] = set()
    for index, notebook in enumerate(notebooks):
        if not isinstance(notebook, dict):
            raise LibraryError(f"notebook at index {index} must be an object")
        missing = [field for field in REQUIRED_FIELDS if field not in notebook]
        if missing:
            raise LibraryError(f"notebook at index {index} missing fields: {', '.join(missing)}")

        notebook_id = notebook["id"]
        if not isinstance(notebook_id, str) or not ID_RE.fullmatch(notebook_id):
            raise LibraryError(f"invalid notebook id: {notebook_id!r}; use kebab-case")
        if notebook_id in RESERVED_IDS:
            raise LibraryError(f"reserved notebook id: {notebook_id!r}")
        if notebook_id in seen:
            raise LibraryError(f"duplicate notebook id: {notebook_id}")
        seen.add(notebook_id)

        for field in ("name", "description"):
            if not isinstance(notebook[field], str) or not notebook[field].strip():
                raise LibraryError(f"{notebook_id}: {field} must be a non-empty string")
        if not is_notebooklm_url(notebook["url"]):
            raise LibraryError(f"{notebook_id}: url must be a NotebookLM URL")
        for field in ("topics", "use_cases"):
            if not isinstance(notebook[field], list) or not all(
                isinstance(item, str) and item.strip() for item in notebook[field]
            ):
                raise LibraryError(f"{notebook_id}: {field} must be an array of non-empty strings")

    if active is not None and active not in seen:
        raise LibraryError(f"active_notebook_id does not exist: {active}")


def is_notebooklm_url(value: Any) -> bool:
    return isinstance(value, str) and NOTEBOOK_URL_RE.match(value) is not None


def find_notebook(data: dict[str, Any], notebook_id: str) -> dict[str, Any]:
    for notebook in data["notebooks"]:
        if notebook["id"] == notebook_id:
            return notebook
    raise LibraryError(f"notebook id not found: {notebook_id}")


def dedupe(values: list[str] | None) -> list[str]:
    result: list[str] = []
    for value in values or []:
        item = value.strip()
        if item and item not in result:
            result.append(item)
    return result


def cmd_validate(args: argparse.Namespace) -> int:
    load_library(args.library)
    print(f"valid: {args.library}")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    data = load_library(args.library)
    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return 0

    notebooks = data["notebooks"]
    active = data["active_notebook_id"]
    if not notebooks:
        print("No notebooks registered.")
        return 0
    for notebook in notebooks:
        marker = "*" if notebook["id"] == active else "-"
        topics = ", ".join(notebook["topics"]) if notebook["topics"] else "no topics"
        print(f"{marker} {notebook['id']} | {notebook['name']} | {topics}")
        print(f"  {notebook['url']}")
        print(f"  {notebook['description']}")
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    data = load_library(args.library)
    if any(notebook["id"] == args.id for notebook in data["notebooks"]):
        raise LibraryError(f"notebook id already exists: {args.id}")
    notebook = {
        "id": args.id,
        "name": args.name,
        "url": canonicalize_notebook_url(args.url),
        "description": args.description,
        "topics": dedupe(args.topic),
        "use_cases": dedupe(args.use_case),
    }
    data["notebooks"].append(notebook)
    write_library(args.library, data)
    print(f"added: {args.id}")
    return 0


def cmd_update(args: argparse.Namespace) -> int:
    data = load_library(args.library)
    notebook = find_notebook(data, args.id)
    for field in ("name", "description"):
        value = getattr(args, field)
        if value is not None:
            notebook[field] = value
    if args.url is not None:
        try:
            notebook["url"] = canonicalize_notebook_url(args.url)
        except LibraryError as exc:
            raise LibraryError(f"{args.id}: {exc}") from exc
    if args.topic is not None:
        notebook["topics"] = dedupe(args.topic)
    if args.use_case is not None:
        notebook["use_cases"] = dedupe(args.use_case)
    write_library(args.library, data)
    print(f"updated: {args.id}")
    return 0


def cmd_set_active(args: argparse.Namespace) -> int:
    data = load_library(args.library)
    if args.clear or args.id == "none":
        if args.id and args.id != "none":
            raise LibraryError("cannot pass both --clear and a notebook id")
        data["active_notebook_id"] = None
        write_library(args.library, data)
        print("active notebook cleared")
        return 0
    if not args.id:
        raise LibraryError("notebook id is required (or pass --clear)")
    find_notebook(data, args.id)
    data["active_notebook_id"] = args.id
    write_library(args.library, data)
    print(f"active notebook: {args.id}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", type=Path, default=DEFAULT_LIBRARY, help="Path to library.json")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="Validate the library file")
    validate.set_defaults(func=cmd_validate)

    list_cmd = subparsers.add_parser("list", help="List registered notebooks")
    list_cmd.add_argument("--json", action="store_true", help="Print the raw library JSON")
    list_cmd.set_defaults(func=cmd_list)

    add = subparsers.add_parser("add", help="Add a notebook")
    add.add_argument("--id", required=True)
    add.add_argument("--name", required=True)
    add.add_argument("--url", required=True)
    add.add_argument("--description", required=True)
    add.add_argument("--topic", action="append", default=[])
    add.add_argument("--use-case", action="append", default=[])
    add.set_defaults(func=cmd_add)

    update = subparsers.add_parser("update", help="Update an existing notebook")
    update.add_argument("id")
    update.add_argument("--name")
    update.add_argument("--url")
    update.add_argument("--description")
    update.add_argument("--topic", action="append")
    update.add_argument("--use-case", action="append")
    update.set_defaults(func=cmd_update)

    active = subparsers.add_parser(
        "set-active",
        help="Set the active notebook, or pass --clear (legacy: pass 'none')",
    )
    active.add_argument("id", nargs="?")
    active.add_argument("--clear", action="store_true", help="Clear the active notebook")
    active.set_defaults(func=cmd_set_active)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except LibraryError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
