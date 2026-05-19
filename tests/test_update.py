import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALL = ROOT / "scripts" / "install.py"
UPDATE = ROOT / "scripts" / "update.py"


def run(cmd, cwd, check=False):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=check)


def sha256_text(value: str):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def init_repo(path: Path):
    run(["git", "init", "-q"], path, check=True)
    (path / "README.md").write_text("# Sample repo\n", encoding="utf-8")
    run(["git", "add", "README.md"], path, check=True)
    run(
        [
            "git",
            "-c",
            "user.name=repo-contract-kit test",
            "-c",
            "user.email=repo-contract-kit@example.invalid",
            "commit",
            "-qm",
            "Initial sample repo",
        ],
        path,
        check=True,
    )


def install_agentic(repo: Path):
    result = run([sys.executable, str(INSTALL), str(repo), "--preset", "agentic"], ROOT)
    if result.returncode != 0:
        raise AssertionError(result.stderr)


def clone_local_kit(tmp_root: Path):
    kit = tmp_root / "repo-contract-kit"
    run(["git", "clone", "-q", str(ROOT), str(kit)], ROOT, check=True)
    return kit


def manifest_path(repo: Path):
    return repo / ".doc-contract-kit" / "manifest.json"


def read_manifest(repo: Path):
    return json.loads(manifest_path(repo).read_text(encoding="utf-8"))


def write_manifest(repo: Path, manifest: dict):
    manifest_path(repo).write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def mark_managed_baseline(repo: Path, rel_path: str, content: str):
    target = repo / rel_path
    target.write_text(content, encoding="utf-8")
    manifest = read_manifest(repo)
    for item in manifest["files"]:
        if item["path"] == rel_path:
            item["installed_sha256"] = sha256_text(content)
            item["managed"] = True
            item["owner"] = "kit"
            break
    write_manifest(repo, manifest)


class UpdateTests(unittest.TestCase):
    def test_clean_managed_file_updates_automatically(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            install_agentic(repo)
            mark_managed_baseline(repo, "AGENTS.md", "# Old managed agents\n")

            result = run([sys.executable, str(UPDATE), str(repo)], ROOT)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotEqual((repo / "AGENTS.md").read_text(encoding="utf-8"), "# Old managed agents\n")
            self.assertIn("# AGENTS.md", (repo / "AGENTS.md").read_text(encoding="utf-8"))
            manifest = read_manifest(repo)
            receipt = json.loads((repo / ".doc-contract-kit" / "install.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["prompt_snapshot"]["name"], "agent-workflow-kit")
            self.assertEqual(
                manifest["prompt_snapshot"]["snapshot_sha256"],
                receipt["prompt_snapshot"]["snapshot_sha256"],
            )

    def test_customized_file_preserves_target_and_writes_conflict_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            install_agentic(repo)
            original = (repo / "AGENTS.md").read_text(encoding="utf-8")
            customized = original + "\nLocal custom instruction.\n"
            (repo / "AGENTS.md").write_text(customized, encoding="utf-8")

            result = run([sys.executable, str(UPDATE), str(repo)], ROOT)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((repo / "AGENTS.md").read_text(encoding="utf-8"), customized)
            reports = sorted((repo / ".doc-contract-kit" / "updates").glob("*/update-report.json"))
            self.assertTrue(reports)
            report = json.loads(reports[-1].read_text(encoding="utf-8"))
            self.assertTrue(any(item["path"] == "AGENTS.md" for item in report["conflicts"]))
            proposed = sorted((repo / ".doc-contract-kit" / "updates").glob("*/proposed/AGENTS.md"))
            self.assertTrue(proposed)

    def test_missing_managed_file_is_restored(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            install_agentic(repo)
            target = repo / "scripts" / "kit_status.py"
            target.unlink()

            result = run([sys.executable, str(UPDATE), str(repo)], ROOT)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(target.exists())

    def test_legacy_install_without_manifest_adopts_without_overwriting(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            install_agentic(repo)
            manifest_path(repo).unlink()
            customized = "# Legacy custom agents\n"
            (repo / "AGENTS.md").write_text(customized, encoding="utf-8")

            result = run([sys.executable, str(UPDATE), str(repo)], ROOT)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Legacy install adopted", result.stdout)
            self.assertEqual((repo / "AGENTS.md").read_text(encoding="utf-8"), customized)
            manifest = read_manifest(repo)
            receipt = json.loads((repo / ".doc-contract-kit" / "install.json").read_text(encoding="utf-8"))
            self.assertIn("agent-workflow-kit", receipt["source_components"])
            self.assertEqual(manifest["prompt_snapshot"]["name"], "agent-workflow-kit")
            agents = next(item for item in manifest["files"] if item["path"] == "AGENTS.md")
            self.assertTrue(agents["managed"])
            self.assertEqual(agents["installed_sha256"], sha256_text(customized))

    def test_dry_run_writes_no_target_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            install_agentic(repo)
            mark_managed_baseline(repo, "AGENTS.md", "# Old managed agents\n")

            result = run([sys.executable, str(UPDATE), str(repo), "--dry-run"], ROOT)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((repo / "AGENTS.md").read_text(encoding="utf-8"), "# Old managed agents\n")
            self.assertFalse(list((repo / ".doc-contract-kit" / "updates").glob("*/update-report.json")))
            self.assertIn('"dry_run": true', result.stdout)

    def test_kit_refresh_refuses_dirty_kit_checkout(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            repo = tmp_root / "target"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)
            kit = clone_local_kit(tmp_root)
            (kit / "DIRTY.txt").write_text("dirty\n", encoding="utf-8")

            result = run(["make", "kit-refresh", f"KIT={kit}"], repo)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Kit checkout has local changes", result.stderr + result.stdout)

    def test_kit_refresh_pulls_status_and_updates(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            repo = tmp_root / "target"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)
            kit = clone_local_kit(tmp_root)

            result = run(["make", "kit-refresh", f"KIT={kit}"], repo)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("repo-contract-kit installed version:", result.stdout)
            self.assertIn("Update complete.", result.stdout)


if __name__ == "__main__":
    unittest.main()
