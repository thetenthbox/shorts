from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from bs4 import BeautifulSoup


@dataclass(frozen=True)
class SceneBuildResult:
    scene_path: Path


def copy_scene_template(*, template_path: Path, out_path: Path) -> SceneBuildResult:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(template_path.read_text(encoding="utf-8"), encoding="utf-8")
    return SceneBuildResult(scene_path=out_path)


def set_html_title(*, html_path: Path, title: str) -> None:
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    title_tag = soup.find("title")
    if not title_tag:
        raise ValueError("No <title> tag found")
    title_tag.string = title
    html_path.write_text(str(soup), encoding="utf-8")


def snapshot_dom_ids(*, html_path: Path) -> Dict[str, int]:
    """Return a count of each id found, to catch duplicates or missing IDs."""
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    counts: Dict[str, int] = {}
    for tag in soup.find_all(attrs={"id": True}):
        _id = tag.get("id")
        counts[_id] = counts.get(_id, 0) + 1
    return counts


