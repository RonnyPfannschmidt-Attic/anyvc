import py
import anyvc

@py.test.mark.files({'setup.py': 'pass'})
@py.test.mark.commit
@py.test.mark.feature('wd:light')
def test_checkout_local(repo, wd, mgr):
    path = mgr.bpath('checkout')

    wd2 = anyvc.workdir.checkout(
        target=path,
        source=repo.path,
        )


@py.test.mark.files({'setup.py': 'pass'})
@py.test.mark.commit
@py.test.mark.feature('wd:heavy')
def test_clone(wd, mgr):

    path = mgr.bpath('clone')

    wd2 = anyvc.workdir.clone(
        target=path,
        source=wd.path,
        )


