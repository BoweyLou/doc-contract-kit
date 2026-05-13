#!/usr/bin/env python3

import argparse
from datetime import datetime, timezone
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import install  # noqa: E402


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc


def write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def run_id():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def manifest_payload(files: list[dict], profiles: list[str], preset: str | None):
    generated_at = now()
    return {
        "schema_version": 1,
        "kit_version": install.read_kit_version(),
        "source_version": install.read_kit_version(),
        "source_ref": install.current_source_ref(),
        "source_components": install.source_components(),
        "prompt_snapshot": install.prompt_snapshot_metadata(),
        "generated_at": generated_at,
        "preset": preset,
        "profiles": profiles,
        "files": files,
    }


def source_metadata(entry: dict):
    source_path = entry["source"]
    return {
        "profile": entry["profile"],
        "source": install.relative_source(source_path),
        "source_sha256": install.sha256_path(source_path),
    }


def write_manifest_payload(target: Path, files: list[dict], profiles: list[str], preset: str | None):
    write_json(target / ".doc-contract-kit" / "manifest.json", manifest_payload(files, profiles, preset))


def resolve_profiles(args, receipt):
    if args.preset:
        class Args:
            preset = args.preset
            profiles = None
            profile = None

        return install.resolve_requested_profiles(Args()), args.preset
    if args.profiles:
        class Args:
            preset = None
            profiles = args.profiles
            profile = None

        return install.resolve_requested_profiles(Args()), None
    if receipt and receipt.get("profiles"):
        return receipt["profiles"], receipt.get("preset")
    return [install.DEFAULT_PROFILE], None


def adoption_files(target: Path, entries: list[dict]):
    files = []
    for rel_target, entry in sorted(install.final_entries_by_target(entries).items()):
        target_path = target / rel_target
        if not target_path.exists():
            continue

        target_owned = rel_target in install.TARGET_OWNED_PATHS
        item = {
            "path": rel_target,
            **source_metadata(entry),
            "installed_sha256": install.sha256_path(target_path),
            "managed": not target_owned,
            "owner": "target" if target_owned else "kit",
        }
        files.append(item)
    return files


def adopt_legacy(target: Path, entries: list[dict], profiles: list[str], preset: str | None):
    write_manifest_payload(target, adoption_files(target, entries), profiles, preset)
    receipt = read_json(target / ".doc-contract-kit" / "install.json") or {}
    receipt.update(
        {
            "schema_version": 1,
            "kit_version": install.read_kit_version(),
            "source_version": install.read_kit_version(),
            "source_ref": install.current_source_ref(),
            "source_components": install.source_components(),
            "prompt_snapshot": install.prompt_snapshot_metadata(),
            "last_updated_at": now(),
            "preset": preset,
            "profiles": profiles,
        }
    )
    receipt.setdefault("installed_at", now())
    receipt["source_commits"] = {
        "repo-contract-kit": install.current_source_ref(),
        "agent-workflow-kit": install.prompt_snapshot_metadata().get("source_ref"),
    }
    write_json(target / ".doc-contract-kit" / "install.json", receipt)
    print("Legacy install adopted. No managed files were overwritten. Re-run update to apply safe updates.")


def copy_proposed(report_dir: Path, rel_target: str, source: Path):
    proposed = report_dir / "proposed" / rel_target
    install.copy_path(source, proposed)
    return proposed


def update_receipt(target: Path, profiles: list[str], preset: str | None):
    path = target / ".doc-contract-kit" / "install.json"
    receipt = read_json(path) or {}
    receipt.update(
        {
            "schema_version": 1,
            "kit_version": install.read_kit_version(),
            "source_version": install.read_kit_version(),
            "source_ref": install.current_source_ref(),
            "source_components": install.source_components(),
            "prompt_snapshot": install.prompt_snapshot_metadata(),
            "last_updated_at": now(),
            "preset": preset,
            "profiles": profiles,
            "source_commits": {
                "repo-contract-kit": install.current_source_ref(),
                "agent-workflow-kit": install.prompt_snapshot_metadata().get("source_ref"),
            },
        }
    )
    receipt.setdefault("installed_at", now())
    write_json(path, receipt)


def write_update_report(report_dir: Path, actions: list[dict], conflicts: list[dict], dry_run: bool):
    payload = {
        "schema_version": 1,
        "generated_at": now(),
        "dry_run": dry_run,
        "actions": actions,
        "conflicts": conflicts,
    }
    write_json(report_dir / "update-report.json", payload)

    lines = [
        "# repo-contract-kit update report",
        "",
        f"- generated_at: {payload['generated_at']}",
        f"- dry_run: {str(dry_run).lower()}",
        f"- actions: {len(actions)}",
        f"- conflicts: {len(conflicts)}",
        "",
        "## Actions",
        "",
    ]
    for action in actions:
        reason = f" - {action['reason']}" if action.get("reason") else ""
        lines.append(f"- {action['action']}: `{action['path']}`{reason}")
    if conflicts:
        lines.extend(["", "## Conflicts", ""])
        for conflict in conflicts:
            proposed = f" Proposed replacement: `{conflict['proposed']}`." if conflict.get("proposed") else ""
            lines.append(f"- `{conflict['path']}` differs from the last managed hash.{proposed}")
    (report_dir / "update-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def merged_manifest_files(target: Path, entries: list[dict], old_files: dict, actions: list[dict]):
    actions_by_path = {action["path"]: action for action in actions}
    files = []
    for rel_target, entry in sorted(install.final_entries_by_target(entries).items()):
        target_path = target / rel_target
        if not target_path.exists():
            continue

        old = old_files.get(rel_target, {})
        action = actions_by_path.get(rel_target, {})
        target_owned = rel_target in install.TARGET_OWNED_PATHS or old.get("owner") == "target"
        old_managed = bool(old.get("managed"))
        action_name = action.get("action")

        if action_name == "conflict" and old_managed:
            item = dict(old)
            item.update({"path": rel_target, **source_metadata(entry), "managed": True, "owner": "kit"})
            files.append(item)
            continue

        managed = not target_owned and (
            old_managed or action_name in {"update", "restore", "force-update"}
        )
        owner = "kit" if managed else "target"
        item = {
            "path": rel_target,
            **source_metadata(entry),
            "installed_sha256": install.sha256_path(target_path),
            "managed": managed,
            "owner": owner,
        }
        files.append(item)
    return files


def apply_update(target: Path, entries: list[dict], manifest: dict, profiles: list[str], preset: str | None, args):
    old_files = {item["path"]: item for item in manifest.get("files", []) if "path" in item}
    final_entries = install.final_entries_by_target(entries)
    actions = []
    conflicts = []
    report_dir = target / ".doc-contract-kit" / "updates" / run_id()

    for rel_target, entry in sorted(final_entries.items()):
        target_path = target / rel_target
        source_path = entry["source"]
        source_sha = install.sha256_path(source_path)
        old = old_files.get(rel_target)
        target_owned = rel_target in install.TARGET_OWNED_PATHS or (old and old.get("owner") == "target")

        if target_owned:
            action_name = "target-owned-missing" if not target_path.exists() else "target-owned"
            actions.append({"path": rel_target, "action": action_name, "managed": False})
            continue

        current_sha = install.sha256_path(target_path) if target_path.exists() else None
        expected_sha = old.get("installed_sha256") if old else None
        clean = target_path.exists() and old and current_sha == expected_sha

        if target_path.exists() and not clean and not args.force_managed:
            action = {
                "path": rel_target,
                "action": "conflict",
                "reason": "target file differs from last managed hash",
                "current_sha256": current_sha,
                "expected_sha256": expected_sha,
            }
            if not args.dry_run:
                proposed = copy_proposed(report_dir, rel_target, source_path)
                action["proposed"] = str(proposed.relative_to(target))
            conflicts.append(action)
            actions.append(action)
            continue

        if target_path.exists() and current_sha == source_sha and not args.force_managed:
            actions.append({"path": rel_target, "action": "current", "managed": True})
            continue

        if args.force_managed and target_path.exists() and not clean:
            action_name = "force-update"
        else:
            action_name = "restore" if not target_path.exists() else "update"
        actions.append({"path": rel_target, "action": action_name, "managed": True})
        if not args.dry_run:
            install.copy_path(source_path, target_path)

    if args.dry_run:
        print(json.dumps({"dry_run": True, "actions": actions}, indent=2, sort_keys=True))
        return

    write_update_report(report_dir, actions, conflicts, dry_run=False)
    if conflicts:
        print(f"Conflicts preserved. Review {report_dir.relative_to(target)}/update-report.md")

    write_manifest_payload(
        target,
        merged_manifest_files(target, entries, old_files, actions),
        profiles,
        preset,
    )
    update_receipt(target, profiles, preset)

    print("Update complete.")
    for action in actions:
        print(f" - {action['action']}: {action['path']}")


def main():
    parser = argparse.ArgumentParser(description="Safely update repo-contract-kit files in a target repo")
    parser.add_argument("target", help="Path to target repository")
    parser.add_argument("--dry-run", action="store_true", help="Print planned actions without writing changes")
    parser.add_argument("--apply", action="store_true", help="Apply safe updates. This is the default.")
    parser.add_argument("--preset", help="Override installed preset")
    parser.add_argument("--profiles", help="Override installed profile list")
    parser.add_argument("--force-managed", action="store_true", help="Overwrite customized kit-managed files")
    args = parser.parse_args()

    target = Path(args.target).expanduser().resolve()
    install.ensure_git_repo(target)
    receipt = read_json(target / ".doc-contract-kit" / "install.json")
    profiles, preset = resolve_profiles(args, receipt)
    entries = install.desired_entries(profiles)
    manifest_path = target / ".doc-contract-kit" / "manifest.json"
    manifest = read_json(manifest_path)

    if manifest is None:
        if args.dry_run:
            print("Legacy install has no manifest. First non-dry run will adopt current files without overwriting.")
            return 0
        adopt_legacy(target, entries, profiles, preset)
        return 0

    apply_update(target, entries, manifest, profiles, preset, args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
