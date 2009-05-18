import py.test

@py.test.mark.xfail("not implemented")
def test_create_repo(mgr):
    repo = mgr.make_repo('repo')
    assert len(repo) == 0
