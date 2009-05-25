"""
    Anyvc bzr repo support

    :license: LGPL 2 or later
    :copyright: 2009 by Ronny Pfannschmidt
"""

from bzrlib.bzrdir import BzrDir
from .base import Repository

class BazaarRepository(Repository):
    def __init__(self, path, create=False):
        if create:
            BzrDir.create_branch_convenience(path)

    def __len__(self):
        return 0

