from anyvc.remote import RemoteBackend


from anyvc.metadata import backends

def pytest_generate_tests(metafunc):
    for backend in backends:
        metafunc.addcall(id=backend, funcargs={'backend': backend})

def test_end_popen_backend(backend):
    backend = RemoteBackend('popen', backend)
    assert backend.active
    backend.stop()
    assert not backend.active



