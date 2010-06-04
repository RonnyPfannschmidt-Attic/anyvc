workdir_class = 'anyvc.bazaar.workdir:Bazaar'
repo_class = 'anyvc.bazaar.repo:BazaarRepository'

features = [
#XXX: make wd without that?
#    'dvcs',
]

def is_workdir(path):
    return path.join('.bzr/checkout').check(dir=1)

def is_repository(path):
    return path.join('.bzr/repository').check(dir=1)
