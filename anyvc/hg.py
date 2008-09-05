# -*- coding: utf-8 -*-
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
"""
    anyvc.mercurial
    ~~~~~~~~~~~~~~~

    Mercurial support

    :license: LGPL3 or later
    :copyright: 2008 Ronny Pfannschmidt
"""

__all__ = 'Mercurial',

import os
from functools import wraps
from .file import StatedPath

try:
        from mercurial import ui, hg
        from mercurial.dispatch import _findrepo
        from mercurial import commands
except ImportError:
    ui, hg, _findrepo = None

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
            print e.hg_output
            raise

    return grabber

class Mercurial(object):

    @staticmethod
    def make_repo(path):
        return Mercurial(path, create=True)

    def __init__(self, path, create=False):
        """
        Get a repo for a given path.
        If `create` is true, a new repo is created.
        """
        self.ui = ui.ui(interactive=False, verbose=True, debug=True)
        if hg is None: 
            # lazy fail so we can import this one and add it to anyvc.all_known
            raise ImportError(
                'no module is named mercurial '
                '(please install mercurial and ensure its in the PYTHONPATH)'
            )
        try:
            self.ui.pushbuffer()
            if not create:
                r = _findrepo(os.path.abspath(path))
                if r is None:
                    raise ValueError('No mercurial repo below %r'%path)
                self.repo = hg.repository(self.ui, r)
            else:
                self.repo = hg.repository(self.ui, path, create=True)

        finally:
            self.__init_out = self.ui.popbuffer()

    def list(self, *k, **kw):
        #XXX: merce conflicts ?!
        names = (
                'modified', 'added', 'removed',
                'deleted', 'unknown', 'ignored', 'clean',
                )
        state_files = self.repo.status(ignored=True, unknown=True, clean=True)
        for state, files in zip(names, state_files):
            for file in files:
                yield StatedPath(file, state, base=self.repo.root)



    @grab_output
    def add(self, paths=()):
        commands.add(self.ui, self.repo, *self.joined(paths))

    def joined(self, paths):
        return [os.path.join(self.repo.root, path) for path in paths]

    @grab_output
    def commit(self, paths=(), message=None, user=None):
        commands.commit(self.ui, self.repo,
            user=user,
            message=message,
            logfile=None,
            date=None,

            *self.joined(paths)
            )


