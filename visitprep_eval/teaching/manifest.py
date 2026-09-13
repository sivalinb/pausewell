"""Reproducibility fingerprints. Never read credentials or environment files."""

from datetime import datetime, timezone
import hashlib
from importlib.metadata import version, PackageNotFoundError
import json
from pathlib import Path
import platform
import subprocess

ROOT = Path(__file__).resolve().parents[2]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fingerprints(paths, root=ROOT):
    return {str(path.relative_to(root)): digest(path) for path in sorted(set(paths)) if path.is_file()}


def build_manifest(output):
    from pausewell.visitprep.provider import build_payload
    output = Path(output).resolve()
    prompt = build_payload([], "Synthetic fingerprint fixture")
    code = list((ROOT / "pausewell").rglob("*.py")) + list((ROOT / "web").rglob("*"))
    evaluators = list((ROOT / "visitprep_eval/teaching").rglob("*.py")) + [
        ROOT / "visitprep_eval/scoring.py", ROOT / "visitprep_eval/run_eval.py",
        ROOT / "scripts/visitprep_utility_comparison.py", ROOT / "scripts/visitprep_integrations.py",
        ROOT / "tests/test_visitprep_replay.py",
    ]
    frozen = [p for directory in ["live", "reliability-retest"]
              for p in (ROOT / "visitprep_eval/reports" / directory).rglob("*") if p.is_file()]
    historical_prompts = {}
    for path in frozen:
        if path.suffix == ".json" and path.parent.name == "cases":
            row = json.loads(path.read_text())
            for index, observation in enumerate(row.get("provider_observations", [])):
                messages = observation.get("request", {}).get("messages", [])
                system = [m for m in messages if m.get("role") == "system"]
                historical_prompts[f"{path.relative_to(ROOT)}#{index}"] = hashlib.sha256(
                    json.dumps(system, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    dependencies = {}
    for name in ["fastapi", "httpx", "pydantic", "langgraph", "langsmith", "pytest", "braintrust"]:
        try:
            dependencies[name] = version(name)
        except PackageNotFoundError:
            dependencies[name] = "not installed"
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip())
    except (OSError, subprocess.CalledProcessError):
        commit, dirty = None, None
    return {
        "schema": "visitprep-teaching-manifest-v1", "generated_at": datetime.now(timezone.utc).isoformat(),
        "checkout_parent_commit": commit, "worktree_dirty": dirty,
        "provenance_notice": "Per-file hashes identify the evaluated worktree; checkout parent is not a claim that uncommitted changes were present in that commit.",
        "application_sha256": fingerprints(code), "evaluator_sha256": fingerprints(evaluators),
        "dataset_sha256": fingerprints([ROOT / "visitprep_eval/cases.json", ROOT / "visitprep_eval/cases-provenance.json", ROOT / "visitprep_eval/teaching/utility_cases.json", ROOT / "visitprep_eval/teaching/acceptance.json", ROOT / "visitprep_eval/teaching/utility_cases_v2_siva.json", ROOT / "visitprep_eval/teaching/acceptance_v2_siva.json"]),
        "baseline_sha256": fingerprints((ROOT / "visitprep_eval/teaching/baselines").glob("*")),
        "dependency_files_sha256": fingerprints([ROOT / "pyproject.toml", ROOT / "requirements.lock"]),
        "runtime": {"python": platform.python_version(), "packages": dependencies},
        "current_prompt_template_sha256": hashlib.sha256(json.dumps(prompt, sort_keys=True, ensure_ascii=False).encode()).hexdigest(),
        "historical_system_prompt_sha256": historical_prompts,
        "captured_artifact_sha256": fingerprints(frozen),
        "generated_artifact_sha256": fingerprints([p for p in output.rglob("*") if p.is_file() and p.name != "manifest.json"], output),
        "manifest_self_hash": "Intentionally excluded to avoid self-reference; all other generated files are covered.",
    }


def verify_artifacts(manifest, output):
    return [name for name, expected in manifest["generated_artifact_sha256"].items()
            if not (Path(output) / name).is_file() or digest(Path(output) / name) != expected]
