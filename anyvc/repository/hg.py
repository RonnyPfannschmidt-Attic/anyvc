"""
    Anyvc Mercurial repository support
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: LGPl 2 or later
    :copyright:
        * 2008 by Ronny Pfannschmidt <Ronny.Pfannschmidt@gmx.de>
"""

from .base import Repository
from ..workdir.hg import grab_output

from mercurial.commands import push

class MercurialRepository(Repository):
    def __init__(self, workdir=None, path=None):
        self.path = path
        self.workdir = workdir
        #XXX: path only handling
        if workdir is not None:
            self.repo = workdir.repo
            self.ui = self.repo.ui

    @grab_output
    def push(self, dest=None, rev=None):
        push(self.ui, self.repo, dest, rev=rev)

    @grab_output
    def pull(self, source="default", rev=None):
        pull(self.ui, self.repo, source, rev=rev)



