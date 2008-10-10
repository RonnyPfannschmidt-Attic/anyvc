# -*- coding: utf-8 -*- 
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
"""
    anyvcs file helpers
    ~~~~~~~~~~~~~~~~~~~

    :copyright: 2006-2008 by Ronny Pfannschmidt

    :license: LGPL2 or later
"""

from os.path import dirname, basename, join

class StatedPath(object):
    """
    stores status informations about files

    >>> StatedPath('a.txt')
    <normal 'a.txt'>
    >>> StatedPath('a.txt', 'changed')
    <changed 'a.txt'>

    """

    def __init__(self, name, state='normal', base=None):
        self.relpath = name
        self.path = dirname(name)
        self.name = basename(name)
        self.base = base
        self.state = intern(state)
        if base is not None:
            self.abspath = join(base, name)
        else:
            self.abspath = None

    def __repr__(self):
        return '<%s %r>'%(
                self.state,
                self.relpath,
                )

    def __str__(self):
        return self.relpath
