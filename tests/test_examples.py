import pytest

from examples.tour import SCENES, execute_scene


@pytest.mark.parametrize("scene", SCENES, ids=lambda scene: scene.slug)
def test_documented_examples_execute(scene):
    outputs = execute_scene(scene)
    assert len(outputs) == len(scene.steps)
    assert all(output for output in outputs)
