import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".agents" / "skills" / "notebooklm" / "scripts" / "library.py"


def run_library(tmp_path, *args):
    library = tmp_path / "library.json"
    if not library.exists():
        library.write_text('{"notebooks": [], "active_notebook_id": null}\n', encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--library", str(library), *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def read_library(tmp_path):
    return json.loads((tmp_path / "library.json").read_text(encoding="utf-8"))


def test_add_list_set_active_update_and_validate(tmp_path):
    added = run_library(
        tmp_path,
        "add",
        "--id",
        "example-research-notebook",
        "--name",
        "Example Research Notebook",
        "--url",
        "https://notebooklm.google.com/notebook/example-notebook",
        "--description",
        "Research notebook about the example topic.",
        "--topic",
        "example-topic",
        "--topic",
        "research-notes",
        "--use-case",
        "answer questions about the example research notes",
    )
    assert added.returncode == 0, added.stderr

    listed = run_library(tmp_path, "list")
    assert listed.returncode == 0, listed.stderr
    assert "example-research-notebook" in listed.stdout
    assert "Example Research Notebook" in listed.stdout

    activated = run_library(tmp_path, "set-active", "example-research-notebook")
    assert activated.returncode == 0, activated.stderr
    assert read_library(tmp_path)["active_notebook_id"] == "example-research-notebook"

    updated = run_library(
        tmp_path,
        "update",
        "example-research-notebook",
        "--description",
        "Updated grounded description.",
        "--topic",
        "wearables",
    )
    assert updated.returncode == 0, updated.stderr
    notebook = read_library(tmp_path)["notebooks"][0]
    assert notebook["description"] == "Updated grounded description."
    assert notebook["topics"] == ["wearables"]

    valid = run_library(tmp_path, "validate")
    assert valid.returncode == 0, valid.stderr


def test_validate_rejects_duplicate_ids(tmp_path):
    library = tmp_path / "library.json"
    entry = {
        "id": "duplicate-id",
        "name": "Notebook",
        "url": "https://notebooklm.google.com/notebook/abc",
        "description": "Description.",
        "topics": [],
        "use_cases": [],
    }
    library.write_text(
        json.dumps({"notebooks": [entry, entry], "active_notebook_id": None}),
        encoding="utf-8",
    )

    result = run_library(tmp_path, "validate")

    assert result.returncode != 0
    assert "duplicate notebook id" in result.stderr


def test_add_canonicalizes_url(tmp_path):
    result = run_library(
        tmp_path,
        "add",
        "--id",
        "canon-url",
        "--name",
        "Canon",
        "--url",
        "https://notebooklm.google.com/notebook/abc123?pli=1&hl=es#section",
        "--description",
        "Canonical URL.",
    )
    assert result.returncode == 0, result.stderr
    notebook = read_library(tmp_path)["notebooks"][0]
    assert notebook["url"] == "https://notebooklm.google.com/notebook/abc123"


def test_update_canonicalizes_url(tmp_path):
    run_library(
        tmp_path,
        "add",
        "--id",
        "canon-update",
        "--name",
        "Canon Update",
        "--url",
        "https://notebooklm.google.com/notebook/initial",
        "--description",
        "Initial.",
    )
    result = run_library(
        tmp_path,
        "update",
        "canon-update",
        "--url",
        "https://notebooklm.google.com/notebook/updated?pli=1#frag",
    )
    assert result.returncode == 0, result.stderr
    notebook = read_library(tmp_path)["notebooks"][0]
    assert notebook["url"] == "https://notebooklm.google.com/notebook/updated"


def test_update_url_error_includes_notebook_id(tmp_path):
    run_library(
        tmp_path,
        "add",
        "--id",
        "ctx",
        "--name",
        "Ctx",
        "--url",
        "https://notebooklm.google.com/notebook/ok",
        "--description",
        "Ok.",
    )
    result = run_library(
        tmp_path,
        "update",
        "ctx",
        "--url",
        "https://example.com/notebook/abc",
    )
    assert result.returncode != 0
    assert "ctx:" in result.stderr
    assert "NotebookLM URL" in result.stderr


def test_set_active_clear_flag(tmp_path):
    run_library(
        tmp_path,
        "add",
        "--id",
        "clearable",
        "--name",
        "Clearable",
        "--url",
        "https://notebooklm.google.com/notebook/clr",
        "--description",
        "Clearable notebook.",
    )
    run_library(tmp_path, "set-active", "clearable")
    assert read_library(tmp_path)["active_notebook_id"] == "clearable"

    cleared = run_library(tmp_path, "set-active", "--clear")
    assert cleared.returncode == 0, cleared.stderr
    assert read_library(tmp_path)["active_notebook_id"] is None


def test_add_rejects_reserved_id_none(tmp_path):
    result = run_library(
        tmp_path,
        "add",
        "--id",
        "none",
        "--name",
        "None",
        "--url",
        "https://notebooklm.google.com/notebook/n",
        "--description",
        "Reserved.",
    )
    assert result.returncode != 0
    assert "reserved notebook id" in result.stderr


def test_set_active_clear_conflicts_with_id(tmp_path):
    run_library(
        tmp_path,
        "add",
        "--id",
        "conflict",
        "--name",
        "Conflict",
        "--url",
        "https://notebooklm.google.com/notebook/conf",
        "--description",
        "Conflict notebook.",
    )
    run_library(tmp_path, "set-active", "conflict")
    result = run_library(tmp_path, "set-active", "--clear", "conflict")
    assert result.returncode != 0
    assert "cannot pass both --clear and a notebook id" in result.stderr
    assert read_library(tmp_path)["active_notebook_id"] == "conflict"


def test_add_rejects_url_with_internal_whitespace(tmp_path):
    result = run_library(
        tmp_path,
        "add",
        "--id",
        "ws-id",
        "--name",
        "WS",
        "--url",
        "https://notebooklm.google.com/notebook/abc trailing",
        "--description",
        "Whitespace.",
    )
    assert result.returncode != 0
    assert "NotebookLM URL" in result.stderr


def test_add_rejects_url_with_extra_path_segments(tmp_path):
    result = run_library(
        tmp_path,
        "add",
        "--id",
        "extra-path",
        "--name",
        "Extra Path",
        "--url",
        "https://notebooklm.google.com/notebook/abc/extra",
        "--description",
        "Extra path.",
    )
    assert result.returncode != 0
    assert "NotebookLM URL" in result.stderr


def test_set_active_none_alias_still_works(tmp_path):
    run_library(
        tmp_path,
        "add",
        "--id",
        "legacy",
        "--name",
        "Legacy",
        "--url",
        "https://notebooklm.google.com/notebook/leg",
        "--description",
        "Legacy notebook.",
    )
    run_library(tmp_path, "set-active", "legacy")
    cleared = run_library(tmp_path, "set-active", "none")
    assert cleared.returncode == 0, cleared.stderr
    assert read_library(tmp_path)["active_notebook_id"] is None


def test_add_rejects_non_notebooklm_url(tmp_path):
    result = run_library(
        tmp_path,
        "add",
        "--id",
        "bad-url",
        "--name",
        "Bad",
        "--url",
        "https://example.com/notebook/abc",
        "--description",
        "Bad URL.",
    )

    assert result.returncode != 0
    assert "NotebookLM URL" in result.stderr
