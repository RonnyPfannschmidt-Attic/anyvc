
from StringIO import StringIO

class MemoryFile(StringIO):
    def __init__(self, data='', path=None):
        StringIO.__init__(self, data)
        self.path = path

    def __enter__(self):
        return self

    def __exit__(self, et, ev, tb):
        pass


class FileBuilder(MemoryFile):
    def __init__(self, repo, base_commit, path):
        MemoryFile.__init__(self, path=path)
        self.repo = repo
        self.base_commit = base_commit

    def __enter__(self):
        return self

    def __exit__(self, et, ev, tb):
        # subvertpy file data transfer doesn't seek back
        self.seek(0)



from os.path import dirname, basename, join, normpath

class StatedPath(object):
    """
    stores status informations about files

    >>> StatedPath('a.txt')
    <normal 'a.txt'>
    >>> StatedPath('a.txt', 'changed')
    <changed 'a.txt'>

    """

    def __init__(self, name, state='normal', base=None):
        self.relpath = normpath(name)
        self.path = dirname(name)
        self.name = basename(name)
        self.base = base
        self.state = intern(state)
        if base is not None:
            self.abspath = join(base, name)
        else:
            self.abspath = None

    def __repr__(self):
        return '<%s %r>'%(
                self.state,
                self.relpath,
                )

    def __str__(self):
        return self.relpath
