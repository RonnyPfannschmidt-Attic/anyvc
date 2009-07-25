"""
    Anyvc Mercurial repository support
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: LGPl 2 or later
    :copyright:
        * 2008 by Ronny Pfannschmidt <Ronny.Pfannschmidt@gmx.de>
"""

from .base import Repository, Revision
from ..workdir.hg import grab_output

from mercurial import commands, localrepo, ui



class MercurialRevision(Revision):
    def __init__(self, repo, rev):
        self.repo, self.rev = repo, rev

    @property
    def message(self):
        return self.rev.description()


class MercurialRepository(Repository):
    def __init__(self, workdir=None, path=None, create=False):
        self.path = path
        self.workdir = workdir
        #XXX: path only handling
        if workdir is not None:
            self.repo = workdir.repo
            self.ui = self.repo.ui

        elif path is not None:
            repo = localrepo.localrepository(ui.ui(), path, create=create)
            self.ui = repo.ui
            self.repo = repo

    def invalidate_cache(self):
        self.repo.invalidate()

    @grab_output
    def push(self, dest=None, rev=None):
        self.invalidate_cache()
        commands.push(self.ui, self.repo, dest, rev=rev)

    @grab_output
    def pull(self, source="default", rev=None):
        self.invalidate_cache()
        commands.pull(self.ui, self.repo, source, rev=rev)

    def __len__(self):
        return 0

    def get_default_head(self):
        self.invalidate_cache()
        return MercurialRevision(self, self.repo['tip'])


