
import py
from anyvc.metadata import backends, get_backend

def test_get_backend(backend, mgr):
    assert backend.module_name == backends[mgr.vc]


def test_has_features(backend):
    assert isinstance(backend.features, set)


def test_has_working_repository_check(mgr, backend):
    mgr.make_repo('repo')
    assert backend.is_repository(mgr.bpath('repo'))


def test_has_working_workdir_check(mgr, backend):
    mgr.create_wd('wd')
    assert backend.is_workdir(mgr.bpath('wd'))
