from agent.timeline_compiler import compile_timeline


def test_compile_builds_schedule():
    tl = {
        "duration_ms": 2000,
        "fps": 30,
        "events": [
            {"t_ms": 0, "op": "layerShow", "target": "a"},
            {"t_ms": 500, "op": "classAdd", "target": "b", "value": "animate"},
            {"t_ms": 500, "op": "classRemove", "target": "c", "value": "x"},
        ],
    }
    compiled = compile_timeline(tl)
    assert compiled.duration_ms == 2000
    assert compiled.fps == 30
    assert 0 in compiled.schedule
    assert 500 in compiled.schedule
    assert len(compiled.schedule[500]) == 2


