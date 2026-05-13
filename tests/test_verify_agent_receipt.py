import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFY = ROOT / "scripts" / "verify_agent_receipt.py"


def valid_receipt():
    return {
        "schema_version": 1,
        "run": {
            "id": "run-test",
            "started_at": "2026-01-01T00:00:00+00:00",
            "completed_at": "2026-01-01T00:01:00+00:00",
            "mode": "verification",
            "status": "pass",
        },
        "tooling": {
            "agent_tool": "manual",
            "agent_tool_version": None,
            "local_only": True,
            "network_used": False,
            "notes": "",
        },
        "scope": {
            "repo_root": ".",
            "base_ref": None,
            "changed_files": ["README.md"],
            "allowed_files": [],
            "protected_files": [],
        },
        "evidence": {
            "files_inspected": ["README.md"],
            "commands": [
                {
                    "command": "python3 scripts/verify_agent_receipt.py --strict --receipt receipt.json",
                    "result": "pass",
                    "exit_code": 0,
                    "notes": "",
                }
            ],
            "docs_impact": {
                "checked": True,
                "result": "pass",
                "categories": [],
                "waiver_reason": None,
            },
            "tests": {
                "result": "not-applicable",
                "failing_test_evidence": None,
                "passing_test_evidence": None,
                "generated_test_provenance": None,
                "skip_reason": "Receipt-only validation; no behavior change under test.",
            },
        },
        "findings": [
            {
                "id": "FINDING_001",
                "priority": "P2",
                "area": "docs",
                "title": "Example finding",
                "confidence": "medium",
                "evidence": ["README.md:1 example"],
                "recommendation": "Review the example.",
                "status": "open",
                "false_positive_notes": "none found",
            }
        ],
        "disposition": {
            "summary": "Validated receipt evidence.",
            "next_actions": [],
            "human_approval_required": False,
        },
    }


class VerifyAgentReceiptTests(unittest.TestCase):
    def test_strict_receipt_passes_with_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            receipt_path = Path(tmp) / "receipt.json"
            receipt_path.write_text(json.dumps(valid_receipt()), encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(VERIFY), "--strict", "--receipt", str(receipt_path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("validation passed", result.stdout)

    def test_strict_receipt_fails_without_required_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            payload = valid_receipt()
            payload["evidence"]["commands"] = []
            payload["evidence"]["docs_impact"]["checked"] = False
            payload["evidence"]["tests"]["skip_reason"] = None
            receipt_path = Path(tmp) / "receipt.json"
            receipt_path.write_text(json.dumps(payload), encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(VERIFY), "--strict", "--receipt", str(receipt_path), "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            output = json.loads(result.stdout)
            self.assertEqual(output["status"], "fail")
            self.assertTrue(any("command" in error for error in output["errors"]))


if __name__ == "__main__":
    unittest.main()
