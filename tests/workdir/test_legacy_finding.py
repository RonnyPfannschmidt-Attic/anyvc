'''
    those tests are for some old apis
    im probably going to deprecate soon
'''
def test_workdir_module_has_all_known():
    from anyvc.workdir import all_known
    assert isinstance(all_known, list)
    #XXX: more?

