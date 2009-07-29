"""
    Anyvc git repo support

    :license: LGPL 2 or later
    :copyright: 2009 by Ronny Pfannschmidt
"""


from .base import Repository, Revision, CommitBuilder, join, DumbFile
import subprocess
import os
from collections import defaultdict
from dulwich.repo import Repo
from dulwich.objects import Blob, Tree, Commit

class GitRevision(Revision):

    def __init__(self, repo, commit):
        self.repo, self.commit = repo, commit

    @property
    def id(self):
        return self.commit.id

    @property
    def parents(self):
        return [GitRevision(self.repo, self.repo.repo.commit(id))
                for id in self.commit.parents]

    @property
    def message(self):
        return self.commit.message.rstrip()

    def __enter__(self):
        return GitRevisionView(self)

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
        #XXX: fragile
        head = self.get_default_head()
        if head is None:
            return 0
        return len(self.repo.revision_history(head.id))

    def push(self):
        #XXX: hell, figure if the remote is empty, push master in that case
        subprocess.check_call(['git', 'push', '--all'], cwd=self.path)

    def get_default_head(self):
        revs = self.repo.get_refs()
        head = revs.get('HEAD', revs.get('master'))
        if head is not None:
            return GitRevision(self, self.repo.get_object(head))

    def transaction(self, **extra):
        return GitCommitBuilder(self, self.get_default_head(), **extra)


class GitCommitBuilder(CommitBuilder):
    def commit(self):
        r = self.repo.repo
        store = r.object_store
        names = sorted(self.files)
        nametree = defaultdict(list)
        for name in names:
            base = name.strip('/')
            while base:
                nbase = os.path.dirname(base)
                nametree[nbase].append(base)
                base = nbase


        tree = Tree()
        for n in names:
            blob = Blob()
            blob.data = self.files[n].content
            store.add_object(blob)
            tree.add(0555, os.path.basename(n), blob.id)
        store.add_object(tree)

        commit = Commit()
        if self.base_commit:
            commit.parents = [self.base_commit.commit.id]
        commit.tree = tree.id
        commit.message = self.extra['message']
        commit.committer = self.extra['author']
        commit.commit_time = 0
        commit.commit_timezone = 0
        commit.author = self.extra['author']
        commit.author_time = 0 #XXX omg
        commit.author_timezone = 0
        store.add_object(commit)
        self.repo.repo.refs['HEAD'] = commit.id


class GitRevisionView(object):
    def __init__(self, revision, path="/"):
        self.revision = revision
        self.path = path
    
    def join(self, path):
        return GitRevisionView(self.revision, join(self.path, path))

    def open(self):
        repo = self.revision.repo.repo
        head = repo['HEAD']
        tree = repo[head.tree]
        #XXX: highly incorrect, should walk and check the type
        blob =repo[tree[self.path.lstrip('/')][1]]

        return DumbFile(blob.data)
