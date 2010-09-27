
import py
from anyvc.metadata import backends, get_backend

def test_get_backend(backend, mgr):
    assert backend.module_name == backends[mgr.vc]


def test_has_features(backend):
    assert isinstance(backend.features, set)


def test_has_working_repository_check(repo, backend):
    print repo.path
    assert backend.is_repository(repo.path)


def test_has_working_workdir_check(wd, backend):
    print wd.path
    assert backend.is_workdir(wd.path)
