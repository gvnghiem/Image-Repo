#!/usr/bin/env python3
"""Scan icon/, photos/, misc/ -> make thumbnails/ and manifest.json.
Run from repo root: python3 scripts/build_manifest.py   (needs Pillow)"""
import json, os, sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
FOLDERS = ["icon", "photos", "misc"]
EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".ico", ".avif"}
THUMB = 360

items = []
for folder in FOLDERS:
    for p in sorted((ROOT / folder).rglob("*")):
        if not p.is_file() or p.suffix.lower() not in EXTS:
            continue
        rel = p.relative_to(ROOT).as_posix()
        entry = {"name": p.stem, "path": rel, "folder": folder,
                 "type": p.suffix.lower().lstrip("."), "bytes": p.stat().st_size}
        if p.suffix.lower() != ".svg":
            try:
                with Image.open(p) as im:
                    entry["width"], entry["height"] = im.size
                    t = ROOT / "thumbnails" / f"{folder}__{p.stem}.webp"
                    if not t.exists() or t.stat().st_mtime < p.stat().st_mtime:
                        th = im.convert("RGBA") if im.mode in ("P", "LA", "RGBA") else im.convert("RGB")
                        th.thumbnail((THUMB, THUMB))
                        th.save(t, "WEBP", quality=82)
                    entry["thumb"] = t.relative_to(ROOT).as_posix()
            except Exception as e:
                print(f"skip thumb for {rel}: {e}", file=sys.stderr)
        items.append(entry)

(ROOT / "manifest.json").write_text(json.dumps({"items": items}, indent=2) + "\n")
print(f"{len(items)} images -> manifest.json")
