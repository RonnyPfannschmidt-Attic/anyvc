
import py
from anyvc.metadata import backends, get_backend

def test_get_backend(mgr):
    vcs = mgr.vc
    mod = get_backend(vcs)
    assert mod.__name__ == backends[vcs]
