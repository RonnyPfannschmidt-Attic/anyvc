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
__all__ = ["all_known", "get_workdir_manager_for_path"]

from .cmdbased import SubVersion, Darcs
from .monotone import Monotone
from .git import Git

all_known = [ SubVersion, Darcs, Git]
unsupported = [ Monotone, ]

try:
    from .hg import Mercurial
    all_known.append(Mercurial)
except ImportError:
    pass

try:
    from .bzr import Bazaar
    all_known.append(Bazaar)
except ImportError:
    pass

def enable_unsupported():
    all_known.extend(unsupported)

def get_workdir_manager_for_path(path):
    found_vcm = None
    for vcm in all_known:
        try:
            vcm_instance = vcm(path) #TODO: this shouldnt need an exception
            if (not found_vcm 
                or len(vcm_instance.base_path) > len(found_vcm.base_path)):
                found_vcm = vcm_instance
        except ValueError:
            pass
    return found_vcm
