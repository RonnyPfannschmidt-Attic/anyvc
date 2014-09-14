

def test_find_repositories(mgr):
    from anyvc import repository
    names = 'fun', 'test', 'oops'
    for name in names:
        mgr.make_repo(name)
    print mgr.base.listdir()

    found_repos = list(repository.find(mgr.base, backends=[mgr.vc]))
    for repo in found_repos:
        print repo
    assert len(found_repos) == len(names)
