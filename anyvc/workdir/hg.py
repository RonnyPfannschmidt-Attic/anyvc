# -*- coding: utf-8 -*-
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
"""
    anyvc.mercurial
    ~~~~~~~~~~~~~~~

    Mercurial support

    :license: LGPL2 or later
    :copyright: 2008 Ronny Pfannschmidt
"""
import os
from functools import wraps

from .file import StatedPath
from .base import WorkDir

from mercurial.__version__ import version as hgversion
# no support for hg <= 1.0.2
if hgversion in ('1.0', '1.0.1', '1.0.2') or hgversion[0]=='0':
    raise ImportError('HG version too old, please update to a release >= 1.1')

from mercurial import ui, hg, commands, util
from mercurial.match import always, exact

__all__ = 'Mercurial',



#XXX: this shouldn't work if used by the vc client
#     console output should be responsive
def grab_output(func):
    """
    wraps a call to hg and grabs the output
    """
    @wraps(func)
    def grabber(self, *k, **kw):
        self.ui.pushbuffer()
        try:
            func(self, *k, **kw)
            return self.ui.popbuffer()
        except Exception, e:
            e.hg_output = self.ui.popbuffer()
            raise

    return grabber


def _find_repo(path):
    last = None
    cur = path
    while cur!=last:
        if os.path.exists(os.path.join(cur, '.hg')):
            return cur
        last = cur
        cur = os.path.dirname(cur)

class Mercurial(WorkDir):

    @staticmethod
    def make_repo(path): #XXX: bullshit here
        return Mercurial(path, create=True)

    def get_repository(self):
        from ..repository.hg import MercurialRepository
        return MercurialRepository(self)

    def __init__(self, path, create=False):
        """
        Get a repo for a given path.
        If `create` is true, a new repo is created.
        """
        self.path = os.path.normpath( os.path.abspath(path) )
        self.ui = ui.ui(interactive=False, verbose=True, debug=True)
        ignored_path = os.environ.get('ANYVC_IGNORED_PATHS', '').split(os.pathsep)
        try:
            self.ui.pushbuffer()
            if not create:
                r = _find_repo(self.path)
                if r is None or r in ignored_path:
                    raise ValueError('No mercurial repo below %r'%path)
                self.base_path = r
                self.repo = hg.repository(self.ui, r)
            else:
                self.base_path = self.path
                self.repo = hg.repository(self.ui, self.path, create=True)

        finally:
            self.__init_out = self.ui.popbuffer()

    def status(self, paths=(), *k, **kw):
        recursive = kw.get('recursive')
        #XXX: merce conflicts ?!
        names = (
                'modified', 'added', 'removed',
                'deleted', 'unknown', 'ignored', 'clean',
                )
        # create a list of files that we are interessted in
        if not kw.get('recursive', True):
            subdir = self.path[len(self.base_path)+1:]
            files = [os.path.join(subdir, x) for x in os.listdir(self.path)]
        else:
            files = ()

        files = () #XXX kill all preselection till i get the matcher interface
        
        if files:
        #XXX: investigate cwd arg
            matcher = exact(self.repo.root, self.repo.root, files)
        else:
            matcher = always(self.repo.root, self.repo.root)
        state_files = self.repo.status(
            match=matcher,
            ignored=True,
            unknown=True,
            clean=True,
        )
        for state, files in zip(names, state_files):
            for file in files:
                yield StatedPath(file, state, base=self.repo.root)



    @grab_output
    def add(self, paths=()):
        commands.add(self.ui, self.repo, *self.joined(paths))

    def joined(self, paths):
        if paths is None:
            return []
        return [os.path.join(self.repo.root, path) for path in paths]

    @grab_output
    def commit(self, paths=(), message=None, user=None):
        commands.commit(self.ui, self.repo,
            user=user,
            message=message,
            logfile=None,
            date=None,
            addremove=False, # only hg 0.9.5 needs that explicit

            *self.joined(paths)
            )

    @grab_output
    def remove(self, paths): 
        #XXX: support for after ?
        commands.remove(self.ui, self.repo,
                after=False, # only hg 0.9.5 needs that explicit
                force=False,
                *self.joined(paths)
                )

    @grab_output
    def revert(self, paths, rev=None): #XXX: how to pass opts['all']?
        if rev is None:
            parents = self.repo.parents()
            if len(parents)!=1 and rev is None:
                #XXX: better exception type?
                raise Exception(
                        "can't revert on top of a merge without explicit rev")
            rev = parents[0].rev()
        commands.revert(self.ui, self.repo,
                date=None,
                rev=rev,
                no_backup=False,
                *self.joined(paths))

    @grab_output
    def rename(self, source, target):
        commands.rename(self.ui, self.repo,
                after=False, # hg 0.9.5
                *self.joined([source, target])
                )

    @grab_output
    def diff(self, paths=(), rev=None):
        commands.diff(
                self.ui,
                self.repo,
                rev=rev,
                git=True,
                *self.joined(paths))




