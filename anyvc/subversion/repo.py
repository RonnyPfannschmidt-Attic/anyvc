"""
    Anyvc svn repo support

    :license: LGPL 2 or later
    :copyright: 2009 by Ronny Pfannschmidt
"""
import sys

from subvertpy import repos, delta
from subvertpy.ra import RemoteAccess, Auth, get_username_provider, SubversionException
from anyvc.common.repository import Repository, Revision, join
from anyvc.common.commit_builder import CommitBuilder
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
        #XXX: jump over irelevant id's
        if self.id == 1:
            return []
        return [SubversionRevision(self.repo, self.id -1)]

    def file_content(self, path):
        try:
            ra = RemoteAccess(self.repo.path)
            import os
            target = StringIO.StringIO()
            ra.get_file(path.lstrip('/'), target, self.id)
            return target.getvalue()
        except: #XXX: bad bad
            raise IOError('%r not found'%path)

    @property
    def message(self):
        ra = RemoteAccess(self.repo.path)
        return ra.rev_proplist(self.id).get('svn:log')

    def get_changed_files(self):
        files = []
        ra = RemoteAccess(self.repo.path)
        def callback(paths, rev, props, childs=None):
            #XXX: take branch path into account?
            files.extend(paths)
        ra.get_log(
            start = self.id,
            end = self.id,
            callback = callback,
            paths = None,
            discover_changed_paths=True)
        return files




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


class SubversionRepository(Repository):

    CommitBuilder = SvnCommitBuilder

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

    def __getitem__(self, id):
        return SubversionRevision(self, id)

