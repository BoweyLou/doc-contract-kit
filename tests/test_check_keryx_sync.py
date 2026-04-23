import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_keryx_sync.py"


def run(cmd, cwd, check=True):
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=check,
    )


def write_repo(repo):
    (repo / ".keryx").mkdir()
    (repo / "docs").mkdir()
    (repo / "src").mkdir()

    (repo / ".keryx" / "config.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "mode": "forced",
                "receipt_path": ".keryx/sync.json",
                "require_receipt_staged": True,
                "keryx_vault_target": "test-vault/project",
                "mirror_paths": [
                    "README.md",
                    "AGENTS.md",
                    "docs/backlog.md",
                    "docs/architecture.md",
                    "docs/plan.md",
                    "docs/documentation-contract.md",
                ],
            }
        ),
        encoding="utf-8",
    )
    (repo / "README.md").write_text("# Test Repo\n", encoding="utf-8")
    (repo / "AGENTS.md").write_text("# AGENTS.md\n", encoding="utf-8")
    (repo / "docs" / "backlog.md").write_text("# Backlog\n", encoding="utf-8")
    (repo / "docs" / "architecture.md").write_text("# Architecture\n", encoding="utf-8")
    (repo / "docs" / "plan.md").write_text("# Plan\n", encoding="utf-8")
    (repo / "docs" / "documentation-contract.md").write_text("# Contract\n", encoding="utf-8")
    (repo / "src" / "app.py").write_text("print('hello')\n", encoding="utf-8")


class KeryxSyncTests(unittest.TestCase):
    def test_write_receipt_then_validate_staged_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            run(["git", "init"], repo)
            write_repo(repo)
            run(["git", "add", "."], repo)

            write_result = run([sys.executable, str(SCRIPT), "--write-receipt", "--source", "keryx-test"], repo)
            self.assertEqual(write_result.returncode, 0, write_result.stderr)
            self.assertTrue((repo / ".keryx" / "sync.json").exists())

            run(["git", "add", ".keryx/sync.json"], repo)
            validate_result = run([sys.executable, str(SCRIPT), "--staged"], repo)

            self.assertEqual(validate_result.returncode, 0, validate_result.stderr)
            self.assertIn("Keryx sync receipt is current.", validate_result.stdout)

    def test_validate_fails_when_receipt_is_not_staged(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            run(["git", "init"], repo)
            write_repo(repo)
            run(["git", "add", "."], repo)

            result = run([sys.executable, str(SCRIPT), "--staged"], repo, check=False)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Keryx sync receipt must be staged", result.stderr)

    def test_validate_fails_when_staged_state_changes_after_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            run(["git", "init"], repo)
            write_repo(repo)
            run(["git", "add", "."], repo)
            run([sys.executable, str(SCRIPT), "--write-receipt", "--source", "keryx-test"], repo)
            run(["git", "add", ".keryx/sync.json"], repo)

            (repo / "src" / "app.py").write_text("print('changed')\n", encoding="utf-8")
            run(["git", "add", "src/app.py"], repo)

            result = run([sys.executable, str(SCRIPT), "--staged"], repo, check=False)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Keryx sync receipt is stale.", result.stdout)
            self.assertIn("staged_tree_hash", result.stdout)


if __name__ == "__main__":
    unittest.main()
