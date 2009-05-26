"""
    Anyvc git repo support

    :license: LGPL 2 or later
    :copyright: 2009 by Ronny Pfannschmidt
"""


from .base import Repository
import subprocess
import os

class GitRepository(Repository):
    def __init__(self, path, create=False):
        if create:
            #XXX: fragile
            if not os.path.exists(path):
                os.mkdir(path)
            subprocess.check_call(['git', 'init'], cwd=path, stdout=None, stdin=None)

    def __len__(self):
        return 0
