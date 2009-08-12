

def test_find_repositories(mgr):
    from anyvc import repository
    names = ['fun','test','oops',]
    repos = [mgr.make_repo(name) for name in names]

    found_repos = list(repository.find(str(mgr.base), backends=[mgr.vc]))
    for repo in found_repos:
        print repo
    assert len(found_repos) == len(names)

