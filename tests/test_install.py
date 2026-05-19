import subprocess
import sys
import tempfile
import unittest
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALL = ROOT / "scripts" / "install.py"


def init_real_git_repo(path: Path):
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    (path / "README.md").write_text("# Sample repo\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=path, check=True)
    subprocess.run(
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
        cwd=path,
        check=True,
    )


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
            self.assertTrue((target / "scripts" / "agent_start.py").exists())
            self.assertTrue((target / "scripts" / "agent_task_prepare.py").exists())
            self.assertTrue((target / "scripts" / "agent_research.py").exists())
            self.assertTrue((target / "scripts" / "classify_review_risk.py").exists())
            self.assertTrue((target / "scripts" / "check_doc_impact.py").exists())
            self.assertTrue((target / "scripts" / "kit_status.py").exists())
            self.assertTrue((target / "REVIEW.md").exists())
            self.assertTrue((target / "scripts" / "version.py").exists())
            self.assertTrue((target / "scripts" / "lint_agent_docs.py").exists())
            self.assertTrue((target / "scripts" / "localize_doc_impact.py").exists())
            self.assertTrue((target / "scripts" / "verify_agent_receipt.py").exists())
            self.assertTrue((target / "schemas" / "session-receipt.schema.json").exists())
            self.assertTrue((target / "schemas" / "review-risk.schema.json").exists())
            self.assertTrue((target / "schemas" / "research-brief.schema.json").exists())
            self.assertTrue((target / "schemas" / "research-source-report.schema.json").exists())
            self.assertTrue((target / "schemas" / "research-synthesis.schema.json").exists())
            self.assertTrue((target / "schemas" / "persona-manifest.schema.json").exists())
            self.assertTrue((target / "schemas" / "agent-permission-policy.schema.json").exists())
            self.assertTrue((target / ".agent-workflows" / "agent-permission-policy.json").exists())
            self.assertTrue((target / ".agent-workflows" / "instruction-budgets.json").exists())
            self.assertTrue((target / ".agent-workflows" / "schemas" / "safe-output.schema.json").exists())
            self.assertTrue((target / ".github" / "workflows" / "agent-review-readonly.yml").exists())
            self.assertTrue((target / "docs" / "ops" / "agent-instruction-hygiene.md").exists())
            self.assertTrue((target / "docs" / "ops" / "agent-tool-network-allowlist.md").exists())
            self.assertTrue((target / ".agent-workflows" / "runs" / ".gitignore").exists())
            self.assertTrue((target / ".agent-workflows" / "tasks" / ".gitignore").exists())
            self.assertTrue((target / ".doc-contract-kit" / "manifest.json").exists())
            self.assertTrue((target / ".doc-contract-kit" / "updates" / ".gitignore").exists())

            receipt = json.loads((target / ".doc-contract-kit" / "install.json").read_text(encoding="utf-8"))
            self.assertIn("source_version", receipt)
            self.assertIn("source_ref", receipt)
            self.assertIn("last_updated_at", receipt)
            self.assertIn("prompt_snapshot", receipt)
            self.assertEqual(receipt["prompt_snapshot"]["name"], "agent-workflow-kit")
            self.assertIn("snapshot_sha256", receipt["prompt_snapshot"])

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
            self.assertIn("repo-contract-kit", receipt["source_commits"])

    def test_install_agentic_preset_writes_commands_and_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_real_git_repo(target)

            result = subprocess.run(
                [sys.executable, str(INSTALL), str(target), "--preset", "agentic"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((target / ".codex" / "prompts" / "multi-agent-repo-review.md").exists())
            self.assertTrue((target / ".codex" / "prompts" / "policies" / "review-risk-classifier.md").exists())
            self.assertTrue((target / ".codex" / "prompts" / "research" / "research-brief.md").exists())
            self.assertTrue((target / ".codex" / "prompts" / "research" / "source-github.md").exists())
            self.assertTrue((target / ".codex" / "prompts" / "research" / "source-arxiv.md").exists())
            self.assertTrue((target / ".codex" / "prompts" / "research" / "source-hacker-news.md").exists())
            self.assertTrue((target / ".codex" / "prompts" / "research" / "source-official-docs.md").exists())
            self.assertTrue((target / ".codex" / "prompts" / "task-packet.md").exists())
            self.assertTrue((target / ".codex" / "prompts" / "templates" / "task-packet.md").exists())
            self.assertTrue((target / ".codex" / "prompts" / "tdd" / "test-quality-sentinel.md").exists())
            self.assertTrue((target / ".agent-workflows" / "README.md").exists())
            self.assertTrue((target / ".agent-workflows" / "repo-review.md").exists())
            self.assertTrue((target / ".agent-workflows" / "schemas" / "session-receipt.schema.json").exists())
            self.assertTrue((target / "schemas" / "task-packet.schema.json").exists())
            self.assertTrue((target / "schemas" / "review-risk.schema.json").exists())
            self.assertTrue((target / "schemas" / "review-synthesis.schema.json").exists())
            self.assertTrue((target / "docs" / "ops" / "agent-workflow.md").exists())
            self.assertTrue((target / "docs" / "ops" / "agent-tool-network-allowlist.md").exists())
            self.assertTrue((target / "docs" / "working-rhythm.md").exists())
            self.assertTrue((target / "VERSION").exists())
            self.assertTrue((target / "CHANGELOG.md").exists())
            self.assertTrue((target / "docs" / "versioning.md").exists())
            readonly_workflow = (target / ".github" / "workflows" / "agent-review-readonly.yml").read_text(encoding="utf-8")
            self.assertIn("persist-credentials: false", readonly_workflow)
            self.assertIn("AGENT_TRUST_PROFILE: untrusted-pr", readonly_workflow)

            makefile = (target / "Makefile").read_text(encoding="utf-8")
            self.assertIn("help: workflow-help", makefile)
            self.assertIn("workflow-help:", makefile)
            self.assertIn("agent-start:", makefile)
            self.assertIn("agent-task-prepare:", makefile)
            self.assertIn("agent-run-review:", makefile)
            self.assertIn("agent-research-plan:", makefile)
            self.assertIn("agent-research-run:", makefile)
            self.assertIn("agent-research-synthesize:", makefile)
            self.assertIn("agent-research-to-task-packet:", makefile)
            self.assertIn("agent-receipt-verify:", makefile)
            self.assertIn("kit-status:", makefile)
            self.assertIn("kit-update:", makefile)
            self.assertIn("agent-review:", makefile)
            self.assertIn("agent-learn:", makefile)
            self.assertIn("agent-review-risk:", makefile)
            self.assertIn("agent-task-packet:", makefile)
            self.assertIn("agent-test-first:", makefile)
            self.assertIn("agent-verify:", makefile)
            self.assertIn("agent-docs-lint:", makefile)
            self.assertIn("agent-docs-localize:", makefile)
            self.assertIn("version-status:", makefile)
            self.assertIn("version-check:", makefile)
            self.assertIn("version-bump:", makefile)

            for target_name in (
                "help",
                "workflow-help",
                "agent-start",
                "agent-run-review",
                "agent-research-plan",
                "agent-research-run",
                "agent-research-synthesize",
                "agent-research-to-task-packet",
                "kit-status",
                "agent-review",
                "agent-learn",
                "agent-review-risk",
                "agent-task-packet",
                "agent-test-first",
                "agent-docs-lint",
                "agent-docs-localize",
                "version-status",
                "version-check",
                "agent-verify",
            ):
                make_result = subprocess.run(
                    ["make", target_name],
                    cwd=target,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(make_result.returncode, 0, make_result.stderr)

                if target_name in {"help", "workflow-help"}:
                    self.assertIn("Orient", make_result.stdout)
                    self.assertIn("Review", make_result.stdout)
                    self.assertIn("Scope", make_result.stdout)
                    self.assertIn("Execute", make_result.stdout)

                if target_name == "agent-start":
                    self.assertIn("Agent start packet written", make_result.stdout)

                if target_name == "agent-review":
                    self.assertIn("Read AGENTS.md, REVIEW.md", make_result.stdout)
                    self.assertIn(".agent-workflows/repo-review.md in bootstrap mode", make_result.stdout)
                    self.assertIn("make agent-run-review AGENT=manual", make_result.stdout)
                    self.assertIn("Produce a findings backlog before editing code", make_result.stdout)

                if target_name == "agent-run-review":
                    self.assertIn("Agent review runner artifacts written", make_result.stdout)
                    run_dirs = [
                        path
                        for path in (target / ".agent-workflows" / "runs").iterdir()
                        if path.is_dir()
                    ]
                    self.assertTrue(run_dirs)
                    latest = sorted(run_dirs)[-1]
                    self.assertTrue((latest / "review-run" / "review-run.json").exists())
                    self.assertTrue((latest / "review-run" / "synthesis" / "review-synthesis.json").exists())

                if target_name == "agent-research-plan":
                    self.assertIn("Research plan written", make_result.stdout)

                if target_name == "agent-research-run":
                    self.assertIn("Source research prompt written", make_result.stdout)

                if target_name == "agent-research-synthesize":
                    self.assertIn("Research synthesis prompt written", make_result.stdout)

                if target_name == "agent-research-to-task-packet":
                    self.assertIn("Research handoff prompt written", make_result.stdout)

                if target_name == "kit-status":
                    self.assertIn("agent-workflow-kit snapshot:", make_result.stdout)
                    self.assertIn("managed file status: clean", make_result.stdout)

            receipt = json.loads((target / ".doc-contract-kit" / "install.json").read_text(encoding="utf-8"))
            self.assertEqual(receipt["preset"], "agentic")
            self.assertEqual(receipt["profiles"], ["minimal", "local-agentic", "review-prompts", "test-first", "versioning"])
            self.assertEqual(receipt["source_version"], (ROOT / "VERSION").read_text(encoding="utf-8").strip())
            snapshot = json.loads((ROOT / "agent-workflow-kit.snapshot.json").read_text(encoding="utf-8"))
            self.assertEqual(receipt["prompt_snapshot"]["source_ref"], snapshot["source_ref"])
            self.assertIn("agent-workflow-kit", receipt["source_components"])
            self.assertEqual(
                receipt["source_commits"]["agent-workflow-kit"],
                snapshot["source_ref"],
            )

            manifest = json.loads((target / ".doc-contract-kit" / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["prompt_snapshot"]["name"], "agent-workflow-kit")
            self.assertEqual(
                manifest["prompt_snapshot"]["snapshot_sha256"],
                receipt["prompt_snapshot"]["snapshot_sha256"],
            )
            manifest_files = {item["path"]: item for item in manifest["files"]}
            self.assertTrue(manifest_files["AGENTS.md"]["managed"])
            self.assertFalse(manifest_files["VERSION"]["managed"])
            self.assertEqual(manifest_files["VERSION"]["owner"], "target")
            self.assertFalse(manifest_files["CHANGELOG.md"]["managed"])
            self.assertEqual(manifest_files["CHANGELOG.md"]["owner"], "target")

    def test_install_agentic_preserves_existing_target_version_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_real_git_repo(target)
            (target / "VERSION").write_text("9.8.7\n", encoding="utf-8")
            (target / "CHANGELOG.md").write_text("# Existing changelog\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(INSTALL), str(target), "--preset", "agentic"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((target / "VERSION").read_text(encoding="utf-8"), "9.8.7\n")
            self.assertEqual((target / "CHANGELOG.md").read_text(encoding="utf-8"), "# Existing changelog\n")

            manifest = json.loads((target / ".doc-contract-kit" / "manifest.json").read_text(encoding="utf-8"))
            manifest_files = {item["path"]: item for item in manifest["files"]}
            self.assertEqual(manifest_files["VERSION"]["owner"], "target")
            self.assertFalse(manifest_files["VERSION"]["managed"])

    def test_install_agentic_agent_start_runs_are_ignored_after_bootstrap_commit(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_real_git_repo(target)

            result = subprocess.run(
                [sys.executable, str(INSTALL), str(target), "--preset", "agentic"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            subprocess.run(["git", "add", "."], cwd=target, check=True)
            subprocess.run(
                [
                    "git",
                    "-c",
                    "user.name=repo-contract-kit test",
                    "-c",
                    "user.email=repo-contract-kit@example.invalid",
                    "commit",
                    "-qm",
                    "Install kit",
                ],
                cwd=target,
                check=True,
            )

            make_result = subprocess.run(
                ["make", "agent-start"],
                cwd=target,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(make_result.returncode, 0, make_result.stderr)
            run_dirs = [
                path
                for path in (target / ".agent-workflows" / "runs").iterdir()
                if path.is_dir()
            ]
            self.assertEqual(len(run_dirs), 1)
            run_dir = run_dirs[0]
            self.assertTrue((run_dir / "agent-brief.md").exists())
            self.assertTrue((run_dir / "session-start.json").exists())
            self.assertTrue((run_dir / "receipt.template.json").exists())

            status = subprocess.run(
                ["git", "status", "--short"],
                cwd=target,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(status.stdout.strip(), "")

    def test_kit_status_compares_against_local_kit(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_real_git_repo(target)

            result = subprocess.run(
                [sys.executable, str(INSTALL), str(target), "--preset", "agentic"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            status = subprocess.run(
                ["make", "kit-status", f"KIT={ROOT}"],
                cwd=target,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(status.returncode, 0, status.stderr)
            self.assertIn("kit update: current", status.stdout)
            self.assertIn("prompt snapshot update: current", status.stdout)

    def test_lint_agent_docs_detects_hidden_unicode(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            bad = target / "AGENTS.md"
            bad.write_text("safe text\u202e\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "lint_agent_docs.py"), "--root", str(target)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("hidden Unicode", result.stdout)

    def test_lint_agent_docs_strict_paths_detects_missing_references(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            (target / "AGENTS.md").write_text("Read `docs/missing.md` first.\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "lint_agent_docs.py"),
                    "--root",
                    str(target),
                    "--strict-paths",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("referenced path does not exist: docs/missing.md", result.stdout)

    def test_lint_agent_docs_detects_unsafe_commands_and_json_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            (target / "AGENTS.md").write_text("Run `git reset --hard` if the agent gets stuck.\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "lint_agent_docs.py"),
                    "--root",
                    str(target),
                    "--format",
                    "json",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "fail")
            self.assertTrue(any(issue["rule_id"] == "git-reset-hard" for issue in payload["issues"]))

    def test_lint_agent_docs_warns_on_contradictory_rules(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            (target / "AGENTS.md").write_text(
                "Do not commit from review mode.\nAgents may commit after review mode.\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "lint_agent_docs.py"),
                    "--root",
                    str(target),
                    "--format",
                    "json",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(any(issue["rule_id"] == "contradiction" for issue in payload["issues"]))

    def test_lint_agent_docs_warns_when_instruction_budget_is_exceeded(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            bullets = "\n".join(
                f"- Agents must follow rule {index} because repeated local failures showed this is needed."
                for index in range(1, 43)
            )
            (target / "AGENTS.md").write_text(f"# AGENTS.md\n\n{bullets}\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "lint_agent_docs.py"),
                    "--root",
                    str(target),
                    "--format",
                    "json",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "pass")
            self.assertTrue(any(issue["rule_id"] == "rule-budget" for issue in payload["issues"]))

    def test_lint_agent_docs_budget_config_can_escalate_to_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            (target / ".agent-workflows").mkdir()
            (target / "AGENTS.md").write_text("# AGENTS.md\n\nMore detail than this repo allows.\n", encoding="utf-8")
            (target / ".agent-workflows" / "instruction-budgets.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "budgets": [
                            {
                                "pattern": "AGENTS.md",
                                "max_lines": 1,
                                "max_rule_bullets": 10,
                                "severity": "error",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "lint_agent_docs.py"),
                    "--root",
                    str(target),
                    "--format",
                    "json",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "fail")
            self.assertTrue(any(issue["rule_id"] == "instruction-budget" for issue in payload["issues"]))

    def test_localize_doc_impact_outputs_json_categories(self):
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "localize_doc_impact.py"),
                "--changed-file",
                "api/users.py",
                "--json",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["result"], "missing-docs")
        self.assertEqual(payload["missing_categories"], ["api"])
        self.assertEqual(payload["categories"][0]["category"], "api")

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
