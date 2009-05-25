"""
    Anyvc svn repo support

    :license: LGPL 2 or later
    :copyright: 2009 by Ronny Pfannschmidt
"""

from subvertpy import repos
from .base import Repository


class SubversionRepository(Repository):

    def __init__(self, path, create=False):
        if create:
            repos.create(path)


    def __len__(self):
        return 0
