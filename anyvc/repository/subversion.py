"""
    Anyvc svn repo support

    :license: LGPL 2 or later
    :copyright: 2009 by Ronny Pfannschmidt
"""
import sys

from subvertpy import repos, delta
from subvertpy.ra import RemoteAccess, Auth, get_username_provider
from .base import Repository, Revision, CommitBuilder, join
import StringIO

class SubversionRevision(Revision):
    def __init__(self, repo, id):
        #XXX: branch subdirs
        self.repo, self.id = repo, id

    @property
    def parents(self):
        #XXX: jup over irelevant id's
        if self.id == 1:
            return []
        return [SubversionRevision(self.repo, self.id -1)]

    def file_content(self, path):
        ra = RemoteAccess(self.repo.path)
        import os
        target = StringIO.StringIO()
        ra.get_file(path.lstrip('/'), target, self.id)
        return target.getvalue()


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
                    self.files[file],
                    txhandler)
            svnfile.close()
        root.close()
        editor.close()


