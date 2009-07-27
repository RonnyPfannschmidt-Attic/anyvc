"""
    Anyvc bzr repo support

    :license: LGPL 2 or later
    :copyright: 2009 by Ronny Pfannschmidt
"""

from bzrlib.bzrdir import BzrDir
from bzrlib.branch import Branch
from .base import Repository, Revision

class BazaarRevision(Revision):
    def __init__(self, repo, bzrrev):
        self.repo, self.bzrrev = repo, bzrrev

    @property
    def message(self):
        return self.bzrrev.message

class BazaarRepository(Repository):
    #XXX: this whole thing is broken and messed
    def __init__(self, path=None, workdir=None, create=False):
        if workdir:
            self.branch = workdir.wt.branch
        #XXX
        if create:
            self.branch = BzrDir.create_branch_convenience(path)

    def __len__(self):
        return 0

    def get_default_head(self):
        revision_id = self.branch.last_revision()
        if revision_id == "null:":
            return
        revision = self.branch.repository.get_revision(revision_id)
        return BazaarRevision(self, revision)


    def push(self, *k, **kw):
        print "bzr push", self.branch.get_parent()
        parent = self.branch.get_parent()
        remote = Branch.open(parent)

        self.branch.push(remote)
