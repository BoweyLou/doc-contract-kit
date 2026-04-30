#!/usr/bin/env python3

import json
from pathlib import Path


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as exc:
        return {"_error": str(exc)}


def main():
    root = Path.cwd()
    receipt = read_json(root / ".doc-contract-kit" / "install.json")
    manifest = read_json(root / ".doc-contract-kit" / "manifest.json")
    version_path = root / "VERSION"
    target_version = version_path.read_text(encoding="utf-8").strip() if version_path.exists() else "missing"

    if not receipt:
        print("repo-contract-kit: not installed or missing .doc-contract-kit/install.json")
        return 1
    if isinstance(receipt, dict) and "_error" in receipt:
        print(f"repo-contract-kit: invalid install receipt: {receipt['_error']}")
        return 1

    print(f"repo-contract-kit installed version: {receipt.get('source_version') or receipt.get('kit_version') or 'unknown'}")
    print(f"source ref: {receipt.get('source_ref') or receipt.get('source_commits', {}).get('repo-contract-kit') or 'unknown'}")
    print(f"preset: {receipt.get('preset') or 'none'}")
    print(f"profiles: {', '.join(receipt.get('profiles', [])) or 'none'}")
    print(f"target repo version: {target_version}")

    if not manifest:
        print("managed manifest: missing")
    elif isinstance(manifest, dict) and "_error" in manifest:
        print(f"managed manifest: invalid: {manifest['_error']}")
        return 1
    else:
        files = manifest.get("files", [])
        managed = sum(1 for item in files if item.get("managed"))
        target_owned = sum(1 for item in files if item.get("owner") == "target")
        print(f"managed manifest: present ({managed} kit-managed, {target_owned} target-owned files)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
