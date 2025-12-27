from pathlib import Path

from agent.scene_builder import copy_scene_template, set_html_title, snapshot_dom_ids


def test_copy_scene_template(tmp_path: Path):
    template = Path(__file__).resolve().parents[1] / "fixtures" / "minimal_template.html"
    out = tmp_path / "out.html"
    res = copy_scene_template(template_path=template, out_path=out)
    assert res.scene_path.exists()
    assert "MINIMAL TEMPLATE" in res.scene_path.read_text(encoding="utf-8")


def test_set_html_title(tmp_path: Path):
    template = Path(__file__).resolve().parents[1] / "fixtures" / "minimal_template.html"
    out = tmp_path / "out.html"
    copy_scene_template(template_path=template, out_path=out)
    set_html_title(html_path=out, title="NewTitle")
    html = out.read_text(encoding="utf-8")
    assert "<title>NewTitle</title>" in html


def test_snapshot_dom_ids_counts(tmp_path: Path):
    html = """<!doctype html><html><head><title>x</title></head><body><div id='a'></div><span id='a'></span></body></html>"""
    p = tmp_path / "x.html"
    p.write_text(html, encoding="utf-8")
    counts = snapshot_dom_ids(html_path=p)
    assert counts["a"] == 2


