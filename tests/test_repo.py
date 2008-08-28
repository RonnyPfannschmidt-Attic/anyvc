from .helpers import for_all
from nose.tools import assert_equal

def initial(mgr):
    mgr.make_repo('repo')
    wd = mgr.make_wd('repo', 'wd')
    wd.put_files(
            ('test.py', 'print "test"'),
            )
    return wd

@for_all
def test_repo(mgr):
    wd = initial(mgr)
    status = list(wd.list(['test.py']))
    print status

    assert_equal(len(status), 1)
    assert_equal(status[0].state, 'unknown')

    wd.add(paths=['test.py'])

    status = list(wd.list(['test.py']))
    print status

    assert_equal(len(status), 1)
    assert_equal(status[0].state, 'added')

    print wd.commit(paths=['test.py'], message='test commit')

    status = list(wd.list(['test.py']))
    print status

    assert_equal(len(status), 1)
    assert_equal(status[0].state, 'clean')


@for_all
def test_repo2(mgr):
    wd = initial(mgr)
    wd.add(paths=['test.py'])
    wd.commit(message='*')
    status = list(wd.list())
    assert_equal(status[0].state, 'clean')


