
import py
from anyvc.metadata import implementations, get_wd_impl, get_repo_impl


def pytest_generate_tests(metafunc):
    for vcs, impls in implementations.items():
        for detail, workdir, repo in impls:
            if workdir or repo:
                metafunc.addcall(
                    id='%s.%s'%(vcs, detail),
                    funcargs=dict(
                        vcs=vcs,
                        detail=detail,
                        wd=workdir,
                        repo=repo,
                        ))


def test_get_wd_impl(vcs, detail, wd, repo):
    if wd is None:
        py.test.skip('no wd implementation for %s/%s availiable'%(vcs, detail))
    impl = get_wd_impl(vcs, detail)
    assert wd.startswith(impl.__module__)
    assert wd.endswith(impl.__name__)


def test_get_repo_impl(vcs, detail, wd, repo):
    if repo is None:
        py.test.skip('no repo implementation for %s/%s availiable'%(vcs, detail))
    impl = get_repo_impl(vcs, detail)
    assert repo.startswith(impl.__module__)
    assert repo.endswith(impl.__name__)
