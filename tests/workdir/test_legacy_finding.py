'''
    those tests are for some old apis
    im probably going to deprecate soon
'''
def test_workdir_module_has_all_known():
    from anyvc.workdir import all_known
    assert isinstance(all_known, list)
    #XXX: more?


def test_get_workdir_manager_for_path(mgr):
    from anyvc.workdir import get_workdir_manager_for_path
    repo = mgr.make_repo('repo')
    wd = mgr.make_wd('repo', 'wd')
    found_wd = get_workdir_manager_for_path(wd.path)
    assert found_wd.path == wd.path
