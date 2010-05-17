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


from .metadata import backends, get_backend
import os

from .common.workdir import find_basepath

def fill(listing):
    for backend in backends:
        try:
            b = get_backend(backend).Workdir
            listing.append(b)
        except: #XXX: diaper antipattern
            pass


class LazyAllKnown(list):
    def __iter__(self):
        if not self:
            fill(self)
        return list.__iter__(self)

all_known = LazyAllKnown()

def get_workdir_manager_for_path(path):
    """
    deprecate
    """
    import warnings
    warnings.warn(
            'get_workdir_manager_for_path is outdated,'
            'please use anyvc.workdir.open',
            DeprecationWarning,
            stacklevel=2)
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


def open(path):
    """
    open a workdir manager for the scm that controlls the given path
    this might be a super
    """
    path = str(path) # so we can use py.path instances
    path = os.path.normpath(path)
    known_backends = [get_backend(bn) for bn in backends]

    res = {}
    for backend in known_backends:
        #XXX: walkdown sould be iterate on same level instead
        #     of walk all per backend
        try:
            base = find_basepath(path, backend.workdir_control)
            if base:
                res[base] = backend
        except AttributeError:
            pass # backend is missing workdir_control
    if res:
        found_backend = res[max(res)] #max gives us the longest path
        return found_backend.Workdir(path)
