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
from posixpath import join
from collections import defaultdict

class Revision(object):
    pass

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
        return CommitBuilder(self, self.get_default_head())


class CommitBuilder(object):
    def __init__(self, repo, base_commit, **extra):
        self.repo = repo
        self.base_commit = base_commit
        self.files = {}


    def filebuilder(self, path):

        if path not in self.files:
            self.files[path] = FileBuilder(self.repo, self.base_commit, path)

        return self.files[path]

    def __enter__(self):
        return RepoPath(self.base_commit, "/", self)

    def __exit__(self, etype, eval, tb):
        pass


class RepoPath(object):
    def __init__(self, commit, path, builder):
        self.commit = commit
        self.path = path
        self.builder = builder


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
        pass

    def __enter__(self):
        return self

    def __exit__(self, et, ev, tb):
        pass
