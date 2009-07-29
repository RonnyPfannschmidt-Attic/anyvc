"""
    Anyvc svn repo support

    :license: LGPL 2 or later
    :copyright: 2009 by Ronny Pfannschmidt
"""
import sys

from subvertpy import repos, delta
from subvertpy.ra import RemoteAccess, Auth, get_username_provider
from .base import Repository, Revision, CommitBuilder, join, DumbFile
import StringIO

class SubversionRevision(Revision):
    def __init__(self, repo, id):
        self.repo, self.id = repo, id

    @property
    def parents(self):
        #XXX: jup over irelevant id's
        if self.id == 1:
            return []
        return [SubversionRevision(self.repo, self.id -1)]

    def __enter__(self):
        return SvnRevisionView(self.repo.path, self.id, '/')


class SubversionRepository(Repository):

    def __init__(self, path, create=False):
        #XXX: correct paths
        if create:
            repos.create(path)
        self.path = "file://"+path



    def __len__(self):
        ra = RemoteAccess(self.path)
        return ra.get_latest_revnum()

    def get_default_head(self):
        #XXX: correct paths !!!
        ra = RemoteAccess(self.path)
        last = ra.get_latest_revnum()
        if last == 0:
            return
        arev = SubversionRevision(self, last)
        arev.message = "broken"
        def cb(changed_paths, rev, revprops, has_children=None):
            arev.message=revprops.get('svn:log')

        ra.get_log(callback=cb, paths=None, start=last-1, end=last)
        return arev

    def transaction(self, **extra):
        return SvnCommitBuilder(self, None, **extra)



class SvnCommitBuilder(CommitBuilder):
    def commit(self):
        ra = RemoteAccess(self.repo.path,
                          auth=Auth([get_username_provider()]))
        editor = ra.get_commit_editor({'svn:log':self.extra['message']})
        root = editor.open_root()
        for file in self.files:
            try:
                svnfile = root.add_file(file)
            except:
                svnfile = root.open_file(file)
            txhandler = svnfile.apply_textdelta()
            delta.send_stream(
                    StringIO.StringIO(self.files[file].content),
                    txhandler)
            svnfile.close()
        root.close()
        editor.close()


class SvnRevisionView(object):
    def __init__(self, base, rev, path):
        self.base = base
        self.rev = rev
        self.path = path

    def join(self, path):
        return SvnRevisionView(self.base, self.rev, join(self.path, path))


    def open(self):
        ra = RemoteAccess(self.base)
        import os
        target = StringIO.StringIO()
        ra.get_file(self.path.lstrip('/'), target, self.rev)
        return DumbFile(target.getvalue())




