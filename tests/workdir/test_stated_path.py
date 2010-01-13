# copyright 2008 by Ronny Pfannschmidt
from anyvc.common.workdir import StatedPath

def test_no_abspath():
    assert StatedPath('a').abspath is None

def test_base_to_abspath():
    assert StatedPath('a', base='b').abspath == 'b/a'

def test_repr():
    assert repr(StatedPath('a')) == "<normal 'a'>"
    assert repr(StatedPath('./a')) == "<normal 'a'>"
