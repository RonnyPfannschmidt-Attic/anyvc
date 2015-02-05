import py
from anyvc.client import style_state, list_colors

items = list(list_colors)


class MockState:
    relpath = '.'

    def __init__(self, state, path='.'):
        self.state = state


@py.test.mark.parametrize('state', items, ids=items)
def test_output_state(state):
    styled = style_state(MockState(state), [])
    assert state.relpath
