import subprocess
import sys
import tempfile
import unittest
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALL = ROOT / "scripts" / "install.py"


class InstallTests(unittest.TestCase):
    def test_install_writes_config_and_skips_existing_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            (target / ".git").mkdir()
            agents = target / "AGENTS.md"
            agents.write_text("existing agents\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(INSTALL), str(target)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(agents.read_text(encoding="utf-8"), "existing agents\n")
            self.assertTrue((target / "doc-contract.json").exists())
            self.assertTrue((target / "scripts" / "check_doc_impact.py").exists())

    def test_install_force_overwrites_existing_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            (target / ".git").mkdir()
            agents = target / "AGENTS.md"
            agents.write_text("existing agents\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(INSTALL), str(target), "--force"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(agents.read_text(encoding="utf-8").startswith("# AGENTS.md"))

    def test_install_rejects_non_git_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()

            result = subprocess.run(
                [sys.executable, str(INSTALL), str(target)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Target is not a git repository", result.stderr)

    def test_install_keryx_forced_profile_writes_forced_sync_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            (target / ".git").mkdir()

            result = subprocess.run(
                [sys.executable, str(INSTALL), str(target), "--profile", "keryx-forced"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((target / ".keryx" / "config.json").exists())
            self.assertTrue((target / ".keryx" / "sync.example.json").exists())
            self.assertTrue((target / "docs" / "backlog.md").exists())
            self.assertTrue((target / "docs" / "architecture.md").exists())
            self.assertTrue((target / "docs" / "plan.md").exists())
            self.assertTrue((target / "scripts" / "check_keryx_sync.py").exists())

            pre_commit = (target / ".pre-commit-config.yaml").read_text(encoding="utf-8")
            self.assertIn("scripts/check_doc_impact.py --staged", pre_commit)
            self.assertIn("scripts/check_keryx_sync.py --staged", pre_commit)

            agents = (target / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("forced Keryx project-state sync", agents)

            makefile = (target / "Makefile").read_text(encoding="utf-8")
            self.assertIn("scripts/check_keryx_sync.py --staged", makefile)

    def test_install_default_profile_does_not_write_keryx_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            (target / ".git").mkdir()

            result = subprocess.run(
                [sys.executable, str(INSTALL), str(target)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((target / ".keryx").exists())
            self.assertFalse((target / "scripts" / "check_keryx_sync.py").exists())

    def test_install_test_first_profile_writes_executable_spec_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            (target / ".git").mkdir()

            result = subprocess.run(
                [sys.executable, str(INSTALL), str(target), "--profile", "test-first"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((target / ".codex" / "prompts" / "tdd" / "README.md").exists())
            self.assertTrue((target / ".codex" / "prompts" / "tdd" / "regression-first-bugfix.md").exists())
            self.assertTrue((target / "docs" / "testing-strategy.md").exists())
            self.assertTrue((target / "docs" / "adr" / "0001-testing-philosophy.md").exists())

            pr_template = (target / ".github" / "pull_request_template.md").read_text(encoding="utf-8")
            self.assertIn("Test-first evidence", pr_template)
            self.assertIn("No tests needed:", pr_template)
            self.assertIn("review docs/testing-strategy.md", result.stdout)

    def test_install_composed_profiles_write_review_and_tdd_prompts(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            (target / ".git").mkdir()

            result = subprocess.run(
                [
                    sys.executable,
                    str(INSTALL),
                    str(target),
                    "--profiles",
                    "review-prompts,test-first",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((target / ".codex" / "prompts" / "multi-agent-repo-review.md").exists())
            self.assertTrue((target / ".codex" / "prompts" / "codebase-learning-comments.md").exists())
            self.assertTrue((target / ".codex" / "prompts" / "personas" / "doc-code-delta.md").exists())
            self.assertTrue((target / ".codex" / "prompts" / "tdd" / "README.md").exists())

            receipt = json.loads((target / ".doc-contract-kit" / "install.json").read_text(encoding="utf-8"))
            self.assertEqual(receipt["profiles"], ["review-prompts", "test-first"])
            self.assertIsNone(receipt["preset"])
            self.assertIn("doc-contract-kit", receipt["source_commits"])

    def test_install_agentic_preset_writes_commands_and_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            (target / ".git").mkdir()

            result = subprocess.run(
                [sys.executable, str(INSTALL), str(target), "--preset", "agentic"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((target / ".codex" / "prompts" / "multi-agent-repo-review.md").exists())
            self.assertTrue((target / ".codex" / "prompts" / "tdd" / "test-quality-sentinel.md").exists())

            makefile = (target / "Makefile").read_text(encoding="utf-8")
            self.assertIn("agent-review:", makefile)
            self.assertIn("agent-learn:", makefile)
            self.assertIn("agent-test-first:", makefile)
            self.assertIn("agent-verify:", makefile)

            for target_name in ("agent-review", "agent-learn", "agent-test-first", "agent-verify"):
                make_result = subprocess.run(
                    ["make", target_name],
                    cwd=target,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(make_result.returncode, 0, make_result.stderr)

            receipt = json.loads((target / ".doc-contract-kit" / "install.json").read_text(encoding="utf-8"))
            self.assertEqual(receipt["preset"], "agentic")
            self.assertEqual(receipt["profiles"], ["minimal", "review-prompts", "test-first"])

    def test_install_strict_agentic_preset_composes_keryx_and_prompt_profiles(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            (target / ".git").mkdir()

            result = subprocess.run(
                [sys.executable, str(INSTALL), str(target), "--preset", "strict-agentic"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((target / ".keryx" / "config.json").exists())
            self.assertTrue((target / ".codex" / "prompts" / "multi-agent-repo-review.md").exists())
            self.assertTrue((target / ".codex" / "prompts" / "tdd" / "README.md").exists())

            makefile = (target / "Makefile").read_text(encoding="utf-8")
            self.assertIn("keryx-check:", makefile)
            self.assertIn("agent-review:", makefile)

            receipt = json.loads((target / ".doc-contract-kit" / "install.json").read_text(encoding="utf-8"))
            self.assertEqual(receipt["preset"], "strict-agentic")
            self.assertEqual(
                receipt["profiles"],
                ["minimal", "review-prompts", "test-first", "keryx-forced"],
            )

    def test_install_rejects_unknown_preset(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            (target / ".git").mkdir()

            result = subprocess.run(
                [sys.executable, str(INSTALL), str(target), "--preset", "missing"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Unknown preset: missing", result.stderr)

    def test_install_rejects_unknown_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            (target / ".git").mkdir()

            result = subprocess.run(
                [sys.executable, str(INSTALL), str(target), "--profile", "missing"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Unknown profile: missing", result.stderr)


if __name__ == "__main__":
    unittest.main()
