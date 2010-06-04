workdir_class = 'anyvc.subversion.workdir:SubVersion'
repo_class = 'anyvc.subversion.repo:SubversionRepository'

def is_workdir(path):
    svn = path.join('.svn')
    return svn.join('entries').check() \
       and svn.join('props').check(dir=1) \
       and svn.join('text-base').check(dir=1)
