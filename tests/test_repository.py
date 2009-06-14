import py.test

def test_repo_create(mgr):
    repo = mgr.make_repo('repo')
    assert len(repo) == 0

def test_repo_default_head(mgr):
    repo = mgr.make_repo('repo')
    wd = mgr.make_wd('repo', 'wd')
    wd.put_files({'test.py': "import sys\nprint sys.platform" })
    wd.add(paths=['test.py'])
    wd.commit(message="test commit")
    #XXX: wrong place for that?
    if wd.repository is not None:
        wd.repository.push()

    for i, message in enumerate(["test commit", "test commit\n", "test\nabc"]):
        wd.put_files({'test.py':'print %s'%i})
        wd.commit(message=message)
        if wd.repository is not None:
            wd.repository.push()
        head = repo.get_default_head()
        print repr(head.message), repr(message)
        #XXX: how to propperly normalize them
        assert head.message.strip()==message.strip()

