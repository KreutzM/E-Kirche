#!/usr/bin/env python3
"""Publish a reproducible inventory of downloaded evidence (no image redistribution)."""
import hashlib
import json
from pathlib import Path

from PIL import Image
from fetch_assets import ROOT, META, allowed, destination


def main():
    manifest = json.loads((ROOT / "data/manifest.json").read_text(encoding="utf-8"))
    metadata = {}
    if META.exists():
        for line in META.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            metadata[row["dataset_id"]] = row
    audit = []
    for row in manifest:
        path = destination(row)
        entry = {"id": row["id"], "commons_page": row["commons_page"], "status": "missing"}
        meta = metadata.get(row["id"])
        if path.exists() and meta:
            with Image.open(path) as image:
                size = list(image.size)
                image.verify()
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            entry.update({key: meta.get(key) for key in (
                "license_short_name", "license_url", "artist", "credit", "retrieved_at",
                "download_url", "downloaded_to", "download_sha256")})
            entry["local_size_px"] = size
            entry["status"] = "verified_download" if digest == meta.get("download_sha256") and allowed(meta.get("license_short_name")) else "invalid"
            entry["visual_review"] = "see docs/iterations/phase_a_001.md; download verification is not geometric validation"
        audit.append(entry)
    target = ROOT / "sources/reference_audit.json"
    target.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Verified downloads: {sum(r['status'] == 'verified_download' for r in audit)}/{len(audit)}")
    return 1 if any(r["status"] == "invalid" for r in audit) else 0


if __name__ == "__main__":
    raise SystemExit(main())
