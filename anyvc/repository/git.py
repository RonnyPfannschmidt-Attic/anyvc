"""
    Anyvc git repo support

    :license: LGPL 2 or later
    :copyright: 2009 by Ronny Pfannschmidt
"""


from .base import Repository
import subprocess
import os

class GitRepository(Repository):
    def __init__(self, path, create=False, bare=False):
        if create:
            #XXX: fragile
            from dulwich.repo import Repo

            if not os.path.exists(path):
                os.mkdir(path)
            Repo.init(path)

    def __len__(self):
        return 0
