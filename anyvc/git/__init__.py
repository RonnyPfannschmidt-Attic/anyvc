repo_class = 'anyvc.git.repo:GitRepository'
workdir_class = 'anyvc.git.workdir:Git'

def is_workdir(path):
    #XXX better check
    return path.join('.git').check(dir=1)
