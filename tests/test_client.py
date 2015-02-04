import py
from anyvc.client import output_state, list_colors

items = list(list_colors)


class MockState:
    relpath = '.'

    def __init__(self, state):
        self.state = state


@py.test.mark.parametrize('state', items, ids=items)
def test_output_state(state):
    output_state(MockState(state), [])
