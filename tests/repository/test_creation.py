import py.test
from datetime import datetime

def test_repo_create(mgr):
    repo = mgr.make_repo('repo')
    default_branch = repo.prepare_default_structure()
    assert len(repo) in (0,1)

def test_repo_default_head(mgr):
    if mgr.vc == 'subversion':
        py.test.skip('default head won\'t matter for svn')
    wd = mgr.create_wd('wd')
    repo = wd.repository
    wd.put_files({'test.py': "import sys\nprint sys.platform" })
    wd.add(paths=['test.py'])
    wd.commit(message="test commit")
    for i, message in enumerate(["test commit", "test commit\n", "test\nabc"]):
        wd.put_files({'test.py':'print %s'%i})
        wd.commit(message=message)
        head = repo.get_default_head()
        print repr(head.message), repr(message)
        #XXX: how to propperly normalize them
        assert head.message.strip()==message.strip()

