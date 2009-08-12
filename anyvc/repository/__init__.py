"""
    Anyvc repo support

    :license: LGPL 2 or later
    :copyright: 2009 by Ronny Pfannschmidt
"""
import os
from ..exc import NotFoundError

def find(base_path, backends=None):
    from anyvc.metadata import get_backends
    for top, dirs, files in os.walk(base_path, topdown=True):
        for backend in get_backends(backends):
            print top
            try:
                yield backend.Repository(top)
                del dirs[:] #XXX: repo found, dont go deeper
            except NotFoundError:
                pass

