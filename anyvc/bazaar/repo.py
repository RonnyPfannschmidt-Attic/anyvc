"""
    Anyvc bzr repo support

    :license: LGPL 2 or later
    :copyright: 2009 by Ronny Pfannschmidt
"""
from bzrlib.bzrdir import BzrDir
from bzrlib.branch import Branch
from bzrlib.memorytree import MemoryTree
from ..repository.base import Repository, Revision, CommitBuilder, join

class BazaarRevision(Revision):
    def __init__(self, repo, bzrrev):
        self.repo, self.bzrrev = repo, bzrrev

    @property
    def parents(self):
        return [ BazaarRevision(self.repo,
                                self.repo.branch.repository.get_revision(rev))
                for rev in self.bzrrev.parent_ids]
    @property
    def message(self):
        return self.bzrrev.message

    def file_content(self, path):
        tree = self.repo.branch.repository.revision_tree(self.bzrrev.revision_id)
        id = tree.path2id(path)
        try:
            tree.lock_read()
            sio = tree.get_file(id)
            return sio.read()
        finally:
            tree.unlock()



class BazaarRepository(Repository):
    #XXX: this whole thing is broken and messed
    def __init__(self, path=None, workdir=None, create=False):
        if workdir:
            self.branch = workdir.wt.branch
        #XXX
        if create:
            self.branch = BzrDir.create_branch_convenience(path)

    def __len__(self):
        #XXX: crap
        revs = self.branch.iter_merge_sorted_revisions()

        return sum(1 for i in revs)

    def get_default_head(self):
        revision_id = self.branch.last_revision()
        if revision_id == "null:":
            return
        revision = self.branch.repository.get_revision(revision_id)
        return BazaarRevision(self, revision)

    def push(self, *k, **kw):
        print "bzr push", self.branch.get_parent()
        parent = self.branch.get_parent()
        remote = Branch.open(parent)

        self.branch.push(remote)

    def transaction(self, **extra):
        return BzrCommitBuilder(self, self.get_default_head(), **extra)

class BzrCommitBuilder(CommitBuilder):
    def __init__(self, *k, **kw):
        super(BzrCommitBuilder, self).__init__(*k, **kw)
        self.tree = MemoryTree.create_on_branch(self.repo.branch)

    def __enter__(self):
        self.tree.lock_write()
        return super(BzrCommitBuilder, self).__enter__()

    def commit(self):
        tree = self.tree
        if tree.path2id('') is None:
            tree.add('')

        for file in self.files:
            print file
            if not tree.path2id(file):
                tree.add(file)
            id = tree.path2id(file)
            tree.put_file_bytes_non_atomic(id, self.files[file].getvalue())

        for old, new in self.renames:
            print old, '->', new
            tree.rename_one(old.lstrip('/'), new.lstrip('/'))


        self.tree.commit(message=self.extra['message'], authors=[self.extra['author']])

    def __exit__(self, et, ev, tb):
        super(BzrCommitBuilder, self).__exit__(et, ev, tb)
        self.tree.unlock()
        self.tree = None

