#!/usr/bin/env python3
"""
build-index.py
Generiert index.json aus allen meta.json Dateien im Hub-Repo.

Usage:
    python3 scripts/build-index.py
"""

import json
import os
from datetime import datetime, timezone

HUB_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_FILE = os.path.join(HUB_ROOT, "index.json")

CONTENT_DIRS = ["agents", "extensions", "tools"]


def main():
    packages = []

    for content_type in CONTENT_DIRS:
        base = os.path.join(HUB_ROOT, content_type)
        if not os.path.isdir(base):
            continue
        for root, dirs, files in os.walk(base):
            if "meta.json" in files:
                meta_path = os.path.join(root, "meta.json")
                try:
                    with open(meta_path) as f:
                        meta = json.load(f)
                    # Relative Pfade zu den Dateien ergänzen
                    rel = os.path.relpath(root, HUB_ROOT)
                    meta["_path"] = rel.replace("\\", "/")
                    packages.append(meta)
                except Exception as e:
                    print(f"WARN: {meta_path}: {e}")

    packages.sort(key=lambda p: (p.get("category", ""), p.get("name", "")))

    index = {
        "version": "1",
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "count": len(packages),
        "packages": packages,
    }

    with open(INDEX_FILE, "w") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    print(f"index.json geschrieben: {len(packages)} Pakete")


if __name__ == "__main__":
    main()
