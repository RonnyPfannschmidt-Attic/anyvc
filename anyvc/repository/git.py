"""
    Anyvc git repo support

    :license: LGPL 2 or later
    :copyright: 2009 by Ronny Pfannschmidt
"""


from .base import Repository, Revision
import subprocess
import os

from dulwich.repo import Repo

class GitRevision(object):

    def __init__(self, repo, commit):
        self.repo, self.commit = repo, commit

    @property
    def message(self):
        return self.commit.message.rstrip()


class GitRepository(Repository):
    def __init__(self, path=None, workdir=None, create=False, bare=False):
        assert path or workdir
        if workdir:
            assert workdir.path
            self.path = workdir.path
        else:
            self.path = path
        if create:
            #XXX: fragile
            if not os.path.exists(path):
                os.mkdir(path)
            self.repo = Repo.init(path)
        else:
            assert os.path.exists(self.path)
            self.repo = Repo(self.path)


    def __len__(self):
        return 0

    def push(self):
        #XXX: hell, figure if the remote is empty, push master in that case
        subprocess.check_call(['git', 'push', '--all'], cwd=self.path)

    def get_default_head(self):
        revs = self.repo.get_refs()
        head = revs.get('HEAD', revs.get('master'))
        if head is not None:
            return GitRevision(self, self.repo.get_object(head))

