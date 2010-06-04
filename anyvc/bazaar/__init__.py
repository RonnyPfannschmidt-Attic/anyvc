workdir_class = 'anyvc.bazaar.workdir:Bazaar'
repo_class = 'anyvc.bazaar.repo:BazaarRepository'

def is_workdir(path):
    print path
    return path.join('.bzr/checkout').check(dir=1)
