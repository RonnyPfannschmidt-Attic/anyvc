repo_class = 'anyvc.mercurial.repo:MercurialRepository'
workdir_class = 'anyvc.mercurial.workdir:Mercurial'

features = [
    'dvcs',
    'wd:heavy',
]



def is_hg(path):
    return path.join('.hg/store').check(dir=1) \
       and path.join('.hg/requires').check()


is_repository = is_workdir = is_hg
