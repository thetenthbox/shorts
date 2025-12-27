from pathlib import Path

from agent.qa import check_assets_exist


def test_check_assets_exist(tmp_path: Path):
    # Create fake asset
    (tmp_path / "img.png").write_bytes(b"x")
    html = """<html><body><img src="img.png"></body></html>"""
    scene = tmp_path / "scene.html"
    scene.write_text(html, encoding="utf-8")
    res = check_assets_exist(scene_path=scene)
    assert res.missing_assets == []


def test_check_assets_missing(tmp_path: Path):
    html = """<html><body><img src="missing.png"></body></html>"""
    scene = tmp_path / "scene.html"
    scene.write_text(html, encoding="utf-8")
    res = check_assets_exist(scene_path=scene)
    assert "missing.png" in res.missing_assets


