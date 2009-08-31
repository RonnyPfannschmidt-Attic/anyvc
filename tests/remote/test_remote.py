import py
from anyvc.remote import RemoteBackend
from anyvc.metadata import backends

def pytest_generate_tests(metafunc):
    if 'backend' not in metafunc.funcargnames:
        return
    for backend in backends:
        metafunc.addcall(id=backend, funcargs={'backend': backend})

def test_end_popen_backend(backend):
    backend = RemoteBackend('popen', backend)
    assert backend.active
    backend.stop()
    assert not backend.active

def test_missing_backend_failure(monkeypatch):
    monkeypatch.setitem(backends, 'testvc', '_missing_._module_')
    print backends
    py.test.raises(ImportError, RemoteBackend, 'popen', 'testvc')
