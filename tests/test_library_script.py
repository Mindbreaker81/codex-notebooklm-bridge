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
        "symptomai-paper",
        "--name",
        "SymptomAI",
        "--url",
        "https://notebooklm.google.com/notebook/81cca36d-c821-4db0-8e67-1b2dfb960eee",
        "--description",
        "Research notebook about SymptomAI.",
        "--topic",
        "health-ai",
        "--topic",
        "symptom-assessment",
        "--use-case",
        "answer questions about SymptomAI evaluation",
    )
    assert added.returncode == 0, added.stderr

    listed = run_library(tmp_path, "list")
    assert listed.returncode == 0, listed.stderr
    assert "symptomai-paper" in listed.stdout
    assert "SymptomAI" in listed.stdout

    activated = run_library(tmp_path, "set-active", "symptomai-paper")
    assert activated.returncode == 0, activated.stderr
    assert read_library(tmp_path)["active_notebook_id"] == "symptomai-paper"

    updated = run_library(
        tmp_path,
        "update",
        "symptomai-paper",
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
