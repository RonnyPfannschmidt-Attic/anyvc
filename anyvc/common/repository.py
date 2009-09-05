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
import time as unixtime
from datetime import datetime
from anyvc.common.files import MemoryFile, FileBuilder

class Revision(object):

    def get_parent_diff(self):
        from anyvc.diff import diff_for_commit
        return diff_for_commit(self)

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

    def read(self):
        return self.revision.file_content(self.path)
    
    def open(self):
        return MemoryFile(self.read(), self.path)

    def isdir(self):
        #XXX: sucks
        try:
            self.listdir()
            return True
        except (IOError, OSError):
            return False

    def isfile(self):
        #XXX: sucks
        try:
            self.open()
            return True
        except (IOError, OSError): #XXX: smarter
            return False

    def exists(self):
        #XXX: sucks
        return self.isdir() or self.isfile()

    exists = isfile #XXX: nasty hack, fix later


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
    #XXX: ugly and inflexible
    '''
    a simple state-tracker
    '''
    def __init__(self, repo, base_commit, time=None, local_time=True, author=None, **extra):
        self.repo = repo
        self.base_commit = base_commit
        self.extra = extra
        self.files = {} #XXX: lossy painfull
        self.renames = []

        if time is None:
            time = datetime.now()
        self.author = author.strip() # normalize whitespace
        self.time = time
        self.time_local = local_time

        timetuple = time.timetuple()

        self.time_unix = unixtime.mktime(timetuple)
        # timetuple[8] is the daylight saving flag
        # its -1 for normal datetimes
        # XXX: the current logic is flawed cause it only thinks about localtime
        # XXX: should it be extended to properly deal
        #      with user defined timezones via pytz/dateutil?
        #if timetuple[8] == 1 and unixtime.daylight:
        #    self.time_offset = unixtime.altzone
        #else:
        #XXX: ignores daylight saving
        self.time_offset = unixtime.timezone

    def create(self, path):
        #XXX: broken model
        if path not in self.files:
            self.files[path] = FileBuilder(self.repo, self.base_commit, path)

        return self.files[path]
    filebuilder = create
    def remove(self, path):
        pass

    def rename(self, source, dest):
        self.renames.append((source, dest))


    def commit(self):
        raise NotImplementedError

    def __enter__(self): 
        return RevisionBuilderPath(self.base_commit, "/", self)

    def __exit__(self, etype,  eval, tb):
        if etype is None: 
            self.commit()


class RevisionBuilderPath( object):
    def __init__( self, commit, path, builder):
        self.commit = commit
        self.path = path
        self.builder = builder

    def rename(self , new_name):
        new = self.parent().join(new_name)
        assert self.path != '/' and new_name != '/'
        self.builder.renames.append( (self.path, new.path))

    def parent(self):
        return RevisionBuilderPath(self.commit, dirname(self.path), self.builder)

    def join(self,  path):
        return RevisionBuilderPath(self.commit, join(self.path, path), self.builder)

    def open(self,  mode='r'):
        if mode ==  'r':
            raise NotImplementedError
        elif mode == 'w':
            return self.builder.filebuilder(self.path)


