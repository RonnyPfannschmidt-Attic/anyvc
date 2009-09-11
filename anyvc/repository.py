"""
    Anyvc repo support

    :license: LGPL 2 or later
    :copyright: 2009 by Ronny Pfannschmidt
"""
import os
from anyvc.exc import NotFoundError

def find(base_path, backends=None):
    from anyvc.metadata import get_backends
    for top, dirs, files in os.walk(base_path, topdown=True):
        for backend in get_backends(backends):
            try:
                yield backend.Repository(top)
                del dirs[:] #XXX: repo found, dont go deeper
            except NotFoundError:
                pass

