"""
    Anyvc svn repo support

    :license: LGPL 2 or later
    :copyright: 2009 by Ronny Pfannschmidt
"""

from subvertpy import repos
from subvertpy.ra import RemoteAccess
from .base import Repository, Revision

class SubversionRevision(object):
    def __init__(self, repo, id):
        self.repo, self.id = repo, id


class SubversionRepository(Repository):

    def __init__(self, path, create=False):
        #XXX: correct paths
        if create:
            repos.create(path)
        self.path = "file://"+path



    def __len__(self):
        return 0

    def get_default_head(self):
        #XXX: correct paths !!!
        ra = RemoteAccess(self.path)
        last = ra.get_latest_revnum()
        if last == 0:
            return
        arev = SubversionRevision(self, last)
        arev.message = "broken"
        def cb(changed_paths, rev, revprops, has_children=None):
            arev.message=revprops['svn:log']

        ra.get_log(callback=cb, paths=None, start=last-1, end=last)
        return arev

