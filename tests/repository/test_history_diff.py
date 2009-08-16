

def test_diff_create_simple(mgr):
    repo = mgr.make_repo('repo')

    with repo.transaction(author='test', message='test') as root:
        with root.join('test.txt').open('w') as f:
            f.write('test')

    head = repo.get_default_head()
    diff = head.get_parent_diff()
    assert '+test' in diff
