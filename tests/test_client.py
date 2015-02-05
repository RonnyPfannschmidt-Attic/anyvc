import pytest
from anyvc.client import style_state, list_colors
from anyvc.common.workdir import StatedPath

items = list(list_colors)


@pytest.mark.parametrize('state', items, ids=items)
def test_output_state(state):
    styled = style_state(StatedPath('.', state), [])
    assert '.' in styled
