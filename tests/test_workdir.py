# copyright 2008 by Ronny Pfannschmidt
# license lgpl2 or later
from .helpers import for_all
from nose.tools import assert_equal
import py.test
from anyvc.exc import NotFoundError
from anyvc.metadata import get_wd_impl

def initial(mgr, commit=False):
    print mgr.make_repo('repo')
    wd = mgr.make_wd('repo', 'wd')
    wd.put_files({
        'test.py':'print "test"',
        })
    assert wd.has_files('test.py')
    if commit:
        wd.add(paths=['test.py'])
        wd.commit(message='*')
    return wd

def test_workdir_add(mgr):
    wd = initial(mgr)
    wd.check_states({
        'test.py': 'unknown',
        })

    print wd.add(paths=['test.py'])

    wd.check_states({
        'test.py': 'added',
        })

    print wd.commit(paths=['test.py'], message='test commit')

    wd.check_states({
        'test.py': 'clean',
        })

def test_subdir_state_add(mgr):
    mgr.make_repo('repo')
    wd = mgr.make_wd('repo', 'wd')
    wd.put_files({
        'subdir/test.py':'test',
    })

    print wd.add(paths=['subdir/test.py'])
    wd.check_states({'subdir/test.py': 'added'}, exact=True)



def test_workdir_remove(mgr):

    wd = initial(mgr, commit=True)
    wd.check_states({
        'test.py': 'clean',
        })
    wd.remove(paths=['test.py'])
    wd.check_states({
        'test.py': 'removed',
        }) 
    wd.commit(message='*')

    py.test.raises(AssertionError,wd.check_states, {'test.py': 'clean'})

def test_workdir_rename(mgr):
    wd = initial(mgr, commit=True)

    wd.rename(source='test.py', target='test2.py')
    wd.check_states({
        'test.py': 'removed',
        'test2.py': 'added',
        })

    wd.commit(message='*')
    wd.check_states({'test2.py': 'clean'})

def test_workdir_revert(mgr):
    wd = initial(mgr, commit=True)

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

def test_diff_all(mgr):
    wd = initial(mgr)
    wd.add(paths=['test.py'])
    wd.commit(message='*')
    wd.put_files({
        'test.py':'ooo'
    })

    diff = wd.diff()
    print diff
    assert 'ooo' in diff
    assert 'print "test"' in diff


def test_file_missing(mgr):
    wd = initial(mgr, commit=True)
    wd.delete_files('test.py')
    wd.check_states({'test.py':'missing'})


def test_handle_not_a_workdir(mgr):
    WD = get_wd_impl(mgr.vc, mgr.detail)
    py.test.raises( NotFoundError, WD,  "/does/not/exist/really")


def test_handle_instanciate_from_subdir(mgr):
    wd = initial(mgr, commit=True)
    WD = get_wd_impl(mgr.vc, mgr.detail)
    test = WD(str(wd.bpath('wd/test.py')))

