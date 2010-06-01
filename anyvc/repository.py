"""
    Anyvc repo support

    :license: LGPL 2 or later
    :copyright: 2009 by Ronny Pfannschmidt
"""
import os
from anyvc.exc import NotFoundError
from py.path import local

def open(path, backends=None):
    """
    open a repository backend at the given path
    """
    from anyvc.metadata import get_backends
    for backend in get_backends(backends):
        try:
            #XXX: add metadata about the worktree base, use it
            return backend.Repository(path)
        except NotFoundError, e:
            pass

def find(root, backends=None):
    """
    :param root: the search root
    :type  root: py.path.local or path string

    find all repositories below :param:`root`
    """
    start = local(root)
    backend = open(root, backends=backends)
    if backend is not None:
        yield backend
    else:
        for subdir in root.listdir(lambda p: p.check(dir=1)):
            for item in find(subdir, backends):
                yield item

