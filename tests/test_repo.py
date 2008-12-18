# copyright 2008 by Ronny Pfannschmidt
# license lgpl3 or later
from .helpers import for_all, disable
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

@disable
@for_all
def test_subdir_state_add(mgr):
    mgr.make_repo('repo')
    wd = mgr.make_wd('repo', 'wd')
    wd.put_files({
        'subdir/test.py':'test',
    })

    wd.add(paths=['subdir/test.py'])
    wd.check_states({'subdir/test.py': 'added'}, exact=True)



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

@for_all
def test_repo_rename(mgr):
    wd = initial(mgr)
    wd.add(paths=['test.py'])
    wd.commit(message='*')

    wd.move(source='test.py', target='test2.py')
    wd.check_states({
        'test.py': 'removed',
        'test2.py': 'added',
        })

    wd.commit(message='*')
    wd.check_states({'test2.py': 'clean'})

@for_all
def test_repo_revert(mgr):
    wd = initial(mgr)
    wd.add(paths=['test.py'])
    wd.commit(message='*')
    wd.remove(paths=['test.py'])
    wd.check_states({'test.py': 'removed'})

    wd.revert(paths=['test.py'])
    wd.check_states({'test.py': 'clean'})

    wd.put_files({
        'test.py':'oooo'
        })

    wd.check_states({'test.py': 'modified'})

    wd.revert(paths=['test.py'])
    wd.check_states({'test.py':'clean'})

