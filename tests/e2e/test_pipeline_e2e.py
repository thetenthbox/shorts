from pathlib import Path

import pytest

from agent.scene_builder import copy_scene_template, set_html_title
from agent.timeline_compiler import compile_timeline


@pytest.mark.e2e
def test_pipeline_e2e_minimal(tmp_path: Path):
    # Minimal e2e: validate timeline + build a scene copy + set title.
    timeline = {
        "duration_ms": 1000,
        "fps": 30,
        "events": [{"t_ms": 0, "op": "layerShow", "target": "x"}],
    }
    compiled = compile_timeline(timeline)
    assert compiled.duration_ms == 1000

    template = Path(__file__).resolve().parents[1] / "fixtures" / "minimal_template.html"
    out = tmp_path / "scene.html"
    copy_scene_template(template_path=template, out_path=out)
    set_html_title(html_path=out, title="E2E")
    assert out.exists()


