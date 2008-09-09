from .helpers import for_all
from nose.tools import assert_equal

def initial(mgr):
    mgr.make_repo('repo')
    wd = mgr.make_wd('repo', 'wd')
    wd.put_files({
        'test.py':'print "test"',
        })
    return wd

@for_all
def test_repo_add(mgr):
    wd = initial(mgr)
    status = list(wd.list(['test.py']))
    wd.check_states({
        'test.py': 'unknown',
        })

    wd.add(paths=['test.py'])

    wd.check_states({
        'test.py': 'added',
        })

    print wd.commit(paths=['test.py'], message='test commit')

    wd.check_states({
        'test.py': 'clean',
        })

@for_all
def test_repo_remove(mgr):
    wd = initial(mgr)
    wd.add(paths=['test.py'])
    wd.commit(message='*')
    wd.check_states({
        'test.py': 'clean',
        })
    wd.remove(paths=['test.py'])
    wd.check_states({
        'test.py': 'removed',
        })
    wd.commit(message='*')
    wd.check_states({'test.py': 'clean'})


