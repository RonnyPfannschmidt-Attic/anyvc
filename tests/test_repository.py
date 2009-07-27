import py.test

def test_repo_create(mgr):
    repo = mgr.make_repo('repo')
    default_branch = repo.prepare_default_structure()
    assert len(repo) in (0,1)

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


def test_build_first_commit(mgr):
    repo = mgr.make_repo('repo')
    with repo.transaction(message='initial', author='test') as root:
        with root.join('test.txt').open('w') as f:
            f.write("text")

    with repo.get_default_head().fs as root:
        with root.join("test.txr").open() as f:
            content = f.read()
            assert content == 'text'

