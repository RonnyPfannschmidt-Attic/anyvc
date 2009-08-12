"""
    Anyvc svn repo support

    :license: LGPL 2 or later
    :copyright: 2009 by Ronny Pfannschmidt
"""
import sys

from subvertpy import repos, delta
from subvertpy.ra import RemoteAccess, Auth, get_username_provider, SubversionException
from ..repository.base import Repository, Revision, CommitBuilder, join
from subvertpy.properties import time_from_cstring, time_to_cstring
import StringIO
from ..exc import NotFoundError


from datetime import datetime


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

    @property
    def message(self):
        ra = RemoteAccess(self.repo.path)
        return ra.rev_proplist(self.id).get('svn:log')

    @property
    def author(self):
        ra = RemoteAccess(self.repo.path)
        return ra.rev_proplist(self.id).get('svn:author')
        

    @property
    def time(self):
        ra = RemoteAccess(self.repo.path)
        date_str = ra.rev_proplist(self.id).get('svn:date')
        timestamp = time_from_cstring(date_str)
        #XXX: subertpy uses a magic factor of 1000000
        return datetime.fromtimestamp(float(timestamp)/1000000)




class SubversionRepository(Repository):

    def __init__(self, path, create=False):
        #XXX: correct paths
        if create:
            repos.create(path)
        self.path = "file://"+path
        try:
            RemoteAccess(self.path)
        except SubversionException:
            raise NotFoundError('subversion', self.path)

    def __len__(self):
        ra = RemoteAccess(self.path)
        return ra.get_latest_revnum()

    def get_default_head(self):
        #XXX: correct paths !!!
        ra = RemoteAccess(self.path)
        last = ra.get_latest_revnum()
        if last == 0:
            return
        return SubversionRevision(self, last)

    def transaction(self, **extra):
        return SvnCommitBuilder(self, None, **extra)



class SvnCommitBuilder(CommitBuilder):
    def commit(self):
        ra = RemoteAccess(self.repo.path,
                          auth=Auth([get_username_provider()]))
        editor = ra.get_commit_editor({
            'svn:log':self.extra['message'],

            #XXX: subertpy uses a magic factor of 1000000
            #XXX: subversion cant set a commit date on commit, sucker
            #'svn:date':time_to_cstring(self.time_unix*1000000),
            })
        print self.time
        root = editor.open_root()

        for src, target in self.renames:
            #XXX: directories
            src = src.lstrip('/')
            target = target.lstrip('/')
            file = root.add_file(target, join(self.repo.path, src), 1)
            file.close()
            root.delete_entry(src)

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


