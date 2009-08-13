import py.test
from datetime import datetime

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

def test_rename_simple(mgr):
    repo = mgr.make_repo('repo')

    with repo.transaction(message='create', author='test') as root:
        with root.join('test.txt').open('w') as f:
            f.write('test')

    with repo.get_default_head() as root:
        assert root.join('test.txt').exists()

    with repo.transaction(message='rename', author='test') as root:
        #XXX: check if relative names are ok for rename in the fs api
        root.join('test.txt').rename('test_renamed.txt')

    with repo.get_default_head() as root:
        assert not root.join('test.txt').exists()
        assert root.join('test_renamed.txt').exists()
