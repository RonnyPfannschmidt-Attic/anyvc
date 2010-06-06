# copyright 2008 by Ronny Pfannschmidt
# license lgpl2 or later
import py.test
from anyvc.exc import NotFoundError
from anyvc.metadata import get_wd_impl


has_files = py.test.mark.files({
        'test.py':'print "test"',
        })

commited = py.test.mark.commit

@has_files
def test_workdir_add(wd):
    wd.check_states(unknown=['test.py'])

    print wd.add(paths=['test.py'])

    wd.check_states(added=['test.py'])

    print wd.commit(paths=['test.py'], message='test commit')

    wd.check_states(clean=['test.py'])

def test_subdir_state_add(wd):
    wd.put_files({
        'subdir/test.py':'test',
    })

    print wd.add(paths=['subdir/test.py'])
    wd.check_states(added=['subdir/test.py'])


@has_files
@commited
def test_workdir_remove(wd):

    wd.check_states(clean=['test.py'])
    wd.remove(paths=['test.py'])
    wd.check_states(removed=['test.py'])
    wd.commit(message='*')

    py.test.raises(AssertionError,wd.check_states, clean='test.py')


@has_files
@commited
def test_workdir_rename(wd):
    wd.rename(source='test.py', target='test2.py')
    wd.check_states(
        removed=['test.py'],
        added=['test2.py'],
    )

    wd.commit(message='*')
    wd.check_states(clean=['test2.py'])


@has_files
@commited
def test_workdir_revert(wd):
    wd.remove(paths=['test.py'])
    wd.check_states(removed=['test.py'])

    wd.revert(paths=['test.py'])
    wd.check_states(clean=['test.py'])

    wd.put_files({
        'test.py':'oooo'
        })

    wd.check_states(modified=['test.py'])

    wd.revert(paths=['test.py'])
    wd.check_states(clean=['test.py'])


@has_files
def test_diff_all(wd):
    wd.add(paths=['test.py'])
    wd.commit(message='*')
    wd.put_files({
        'test.py':'ooo'
    })

    diff = wd.diff()
    print diff
    assert 'ooo' in diff
    assert 'print "test"' in diff


@has_files
@commited
def test_file_missing(wd):
    wd.delete_files('test.py')
    wd.check_states(missing=['test.py'])


@has_files
@commited
def test_status_subdir_only(wd):
    wd.put_files({
        'subdir/a.py':'foo\n',
        })
    wd.add(paths=['subdir/a.py'])
    wd.check_states(added=['subdir/a.py'])

    print wd.commit(message='add some subdir')

    wd.check_states(clean=['subdir/a.py'])
    wd.put_files({
        'subdir/a.py':'bar\nfoo\n', #XXX: different size needed for hg status
        })

    stats = list(wd.status(paths=['subdir']))
    assert any(s.relpath == 'subdir/a.py' for s in stats)

    wd.check_states(modified=['subdir/a.py'])


@has_files
@commited
def test_workdir_open(wd, backend):
    import anyvc
    wd2 = anyvc.workdir.open(wd.bpath(''))
    assert backend.is_workdir(wd2.path)


