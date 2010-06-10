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

import warnings

from .metadata import get_backends
import os
from py.path import local
from .common.workdir import find_basepath

def open(path):
    """
    :param path:
        a local path to the worktree
        preferable a `py.path.local` instance

    open a scm workdir

    It uses the backend metadata to find the correct backend and
    won't import unnecessary backends to keep the import time low
    """

    for part in local(path).parts(reverse=True):
        applying = [ backend for backend in get_backends()
                     if backend.is_workdir(part) ]

        if applying:
            if len(applying) > 1:
                warnings.warn('found more than one backend below %s' % part)
            return applying[0].Workdir(part)



def clone(source, target):
    """
    create a heavy checkout/clone of the given source
    """
    #XXX: remote support
    for backend in get_backends():
        if 'wd:heavy' in backend.features and backend.is_repository(source):
            return backend.Workdir(target, create=True, source=source)


def checkout(source, target):
    """
    create a light checkout of the given source
    """
    #XXX: remote support
    for backend in get_backends():
        if 'wd:light' in backend.features and backend.is_repository(source):
            #XXX: there should be an actual argument
            #     to keep heavy and light apart
            return backend.Workdir(target, create=True, source=source)
