# -*- coding: utf-8 -*- 
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
"""
    anyvc
    ~~~~~

    Simple vcs abstraction.

    :license: LGPL2 or later
    :copyright:
        * 2006 Ali Afshar aafshar@gmail.com
        * 2008 Ronny Pfannschmidt Ronny.Pfannschmidt@gmx.de
"""
__all__ = ["all_known"]

from .cmdbased import Bazaar, SubVersion, Darcs, Git
from .monotone import Monotone
from .hg import Mercurial

all_known = [ Monotone, Bazaar, SubVersion, Mercurial, Darcs, Git]
