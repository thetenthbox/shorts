from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List


ASSET_RE = re.compile(r"""(?:src|href)=(?:"([^"]+)"|'([^']+)')""")


@dataclass(frozen=True)
class QAResult:
    missing_assets: List[str]


def find_asset_refs(html: str) -> List[str]:
    refs: List[str] = []
    for m in ASSET_RE.finditer(html):
        refs.append(m.group(1) or m.group(2))
    return refs


def check_assets_exist(*, scene_path: Path) -> QAResult:
    html = scene_path.read_text(encoding="utf-8")
    refs = find_asset_refs(html)

    missing: List[str] = []
    for ref in refs:
        # ignore absolute URLs
        if ref.startswith("http://") or ref.startswith("https://"):
            continue
        # resolve relative to scene file
        p = (scene_path.parent / ref).resolve()
        if not p.exists():
            missing.append(ref)
    return QAResult(missing_assets=missing)


