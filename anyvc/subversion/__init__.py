workdir_class = 'anyvc.subversion.workdir:SubVersion'
repo_class = 'anyvc.subversion.repo:SubversionRepository'

features = [
    'wd:light',
]


def is_workdir(path):
    svn = path.join('.svn')
    return svn.join('entries').check() \
       and svn.join('props').check(dir=1) \
       and svn.join('text-base').check(dir=1)

def is_repository(path):
    return path.join('format').check() \
       and path.join('hooks').check(dir=1) \
       and path.join('locks').check(dir=1) \
       and path.join('format').read().strip().isdigit()
