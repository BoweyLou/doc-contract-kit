import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALL = ROOT / "scripts" / "install.py"


def run(cmd, cwd, check=False):
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=check,
    )


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
    run(["git", "add", "."], repo, check=True)
    run(
        [
            "git",
            "-c",
            "user.name=repo-contract-kit test",
            "-c",
            "user.email=repo-contract-kit@example.invalid",
            "commit",
            "-qm",
            "Install repo contract kit",
        ],
        repo,
        check=True,
    )


class AgentTaskPrepareTests(unittest.TestCase):
    def test_prepare_creates_sibling_worktree_and_local_task_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)

            result = run(
                ["make", "agent-task-prepare", "TASK=AGW-061", "TITLE=Add task launcher", "SCOPE=scripts/agent_task_prepare.py"],
                repo,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Agent task worktree prepared", result.stdout)

            metadata = json.loads((repo / ".agent-workflows" / "tasks" / "agw-061.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["task_id"], "AGW-061")
            self.assertEqual(metadata["status"], "in-progress")
            self.assertEqual(metadata["scope"], ["scripts/agent_task_prepare.py"])
            self.assertTrue(metadata["branch"].startswith("codex/task-agw-061-"))

            worktree = Path(metadata["worktree"])
            self.assertTrue(worktree.exists())
            self.assertFalse(str(worktree).startswith(str(repo / ".agent-workflows")))
            packet = json.loads((worktree / metadata["task_packet"]).read_text(encoding="utf-8"))
            receipt = json.loads((worktree / metadata["receipt_template"]).read_text(encoding="utf-8"))
            self.assertEqual(packet["task"]["id"], "AGW-061")
            self.assertEqual(packet["scope"]["allowed_files"], ["scripts/agent_task_prepare.py"])
            self.assertEqual(receipt["review_risk"]["trust_profile"], "write-worker")

            status = run(["git", "status", "--short"], repo)
            self.assertEqual(status.stdout.strip(), "")

    def test_prepare_blocks_overlapping_scope_when_requested(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)

            first = run(["make", "agent-task-prepare", "TASK=AGW-061", "SCOPE=scripts"], repo)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)

            second = run(
                ["make", "agent-task-prepare", "TASK=AGW-062", "SCOPE=scripts/agent_task_prepare.py", "OVERLAP=block"],
                repo,
            )

            self.assertNotEqual(second.returncode, 0)
            self.assertIn("overlaps an in-flight task", second.stderr)

    def test_prepare_requires_clean_main_checkout_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)
            (repo / "README.md").write_text("# Dirty repo\n", encoding="utf-8")

            result = run(["make", "agent-task-prepare", "TASK=AGW-061"], repo)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Main checkout must be clean", result.stderr)


if __name__ == "__main__":
    unittest.main()
