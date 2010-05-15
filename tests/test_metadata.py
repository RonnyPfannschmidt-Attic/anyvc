
import py
from anyvc.metadata import backends, get_backend

def test_get_backend(mgr):
    vcs = mgr.vc
    backend = get_backend(vcs)
    assert backend.module.__name__ == backends[vcs]
