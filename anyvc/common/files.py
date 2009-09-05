
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
