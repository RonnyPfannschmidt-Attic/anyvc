"""
    Anyvc Repository Base Classes
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Various base classes for dealing with history data

    :license: LGPl 2 or later
    :copyright:
        * 2008 by Ronny Pfannschmidt <Ronny.Pfannschmidt@gmx.de>

    .. warning::

        the repo apis are unstable and incomplete

"""
from posixpath import join, basename, dirname
from collections import defaultdict
from StringIO import StringIO

class MemoryFile(StringIO):
    def __init__(self, data='', path=None):
        StringIO.__init__(self, data)
        self.path = path

    def __enter__(self):
        return self

    def __exit__(self, et, ev, tb):
        pass

class Revision(object):
    def __enter__(self):
       return RevisionView(self, '/')

    def __exit__(self, et, ev, tb):
        pass

class RevisionView(object):
    def __init__(self, revision, path):
        self.revision = revision
        self.path = path

    def join(self, path):
        return RevisionView(self.revision, join(self.path, path))

    def open(self):
        return MemoryFile(self.revision.file_content(self.path))

    def isdir(self):
        #XXX: sucks
        try:
            self.listdir()
            return True
        except: #XXX: smarter
            return False

    def isfile(self):
        #XXX: sucks
        try:
            self.open()
            return True
        except: #XXX: smarter
            return False

    def exists(self):
        #XXX: sucks
        return self.isdir() or self.isfile()


class Repository(object):
    """
    represents a repository
    """

    local = True

    def __init__(self,**extra):
        self.path = path
        self.extra = extra

    def prepare_default_structure(self):
        """
        if the vcs has a common standard repo structure, set it up
        """
        pass

    def push(self, dest=None, rev=None):
        """
        push to a location

        :param dest: the destination
        :param rev: the maximum revision to push, may be none for latest
        """
        raise NotImplementedError("%r doesnt implement push"%self.__class__)

    def pull(self, source=None, rev=None):
        """
        counterpart to push
        """
        raise NotImplementedError("%r doesnt implement pull"%self.__class__)


    def transaction(self, **extra):
        return CommitBuilder(self, self.get_default_head(), **extra)


class CommitBuilder(object):
    def __init__(self, repo, base_commit, **extra):
        self.repo = repo
        self.base_commit = base_commit
        self.extra = extra
        self.files = {} #XXX: lossy painfull
        self.renames = []


    def create(self, path):
        #XXX: broken model
        if path not in self.files:
            self.files[path] = FileBuilder(self.repo, self.base_commit, path)

        return self.files[path]
    filebuilder = create
    def remove(self, path):
        pass

    def rename(self, source, dest):
        pass


    def commit(self):
        raise NotImplementedError

    def __enter__(self):
        return RepoPath(self.base_commit, "/", self)

    def __exit__(self, etype, eval, tb):
        if etype is None:
            self.commit()


class RepoPath(object):
    def __init__(self, commit, path, builder):
        self.commit = commit
        self.path = path
        self.builder = builder

    def rename(self, new_name):
        new = self.parent().join(new_name)
        assert self.path != '/' and new_name != '/'
        self.builder.renames.append( (self.path, new.path))

    def parent(self):
        return RepoPath(self.commit, dirname(self.path), self.builder)

    def join(self, path):
        return RepoPath(self.commit, join(self.path, path), self.builder)

    def open(self, mode='r'):
        if mode == 'r':
            raise NotImplementedError
        elif mode == 'w':
            return self.builder.filebuilder(self.path)

class FileBuilder(object):
    def __init__(self, repo, base_commit, path):
        self.repo = repo
        self.base_commit = base_commit
        self.path = path
        self.content = None

    def write(self, data):
        #XXX: no im not kidding, just lazy
        self.content = data

    def __enter__(self):
        return self

    def __exit__(self, et, ev, tb):
        pass
