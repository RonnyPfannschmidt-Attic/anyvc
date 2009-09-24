"""
    Anyvc bzr repo support

    :license: LGPL 2 or later
    :copyright: 2009 by Ronny Pfannschmidt
"""
from bzrlib.bzrdir import BzrDir
from bzrlib.branch import Branch
from bzrlib import errors
from bzrlib.memorytree import MemoryTree
from anyvc.common.repository import Repository, Revision, join
from anyvc.common.commit_builder import CommitBuilder
from datetime import datetime
from ..exc import NotFoundError

class BazaarRevision(Revision):
    def __init__(self, repo, bzrrev):
        self.repo, self.bzrrev = repo, bzrrev

    @property
    def id(self):
        return self.bzrrev.revision_id

    def get_changed_files(self):
        # TODO: this doesn't yet handle the case of multiple parent revisions
        #XXX: handle first commit beter
        rev = self.bzrrev
        repo = self.repo.branch.repository

        current = repo.revision_tree(rev.revision_id)
        if self.parents:
            prev = repo.revision_tree(rev.parent_ids[0])
        else:
            prev = repo.revision_tree('null:')
        delta = current.changes_from(prev)
        files = [f[0] for f in delta.added + delta.removed + delta.renamed + delta.kind_changed + delta.modified]
        return files


        # diff_file is a stringio
        #diff_tree = diff.DiffTree(prev, current, diff_file)

        #self._branch.lock_read()
        #diff_tree.show_diff('')
        #self._branch.unlock()



    @property
    def time(self):
        return datetime.fromtimestamp(self.bzrrev.timestamp)

    @property
    def parents(self):
        return [ BazaarRevision(self.repo,
                                self.repo.branch.repository.get_revision(rev))
                for rev in self.bzrrev.parent_ids]
    @property
    def message(self):
        return self.bzrrev.message

    @property
    def author(self):
        return self.bzrrev.get_apparent_author()

    def file_content(self, path):
        tree = self.repo.branch.repository.revision_tree(self.bzrrev.revision_id)
        id = tree.path2id(path)
        if id is None:
            raise IOError('%r not found'%path)
        try:
            tree.lock_read()
            sio = tree.get_file(id)
            return sio.read()
        finally:
            tree.unlock()

    def exists(self, path):
        tree = self.repo.branch.repository.revision_tree(self.bzrrev.revision_id)
        return tree.path2id(path) is not None



class BazaarCommitBuilder(CommitBuilder):
    def __init__(self, *k, **kw):
        super(BazaarCommitBuilder, self).__init__(*k, **kw)
        self.tree = MemoryTree.create_on_branch(self.repo.branch)

    def __enter__(self):
        self.tree.lock_write()
        if self.tree.path2id('') is None:
            self.tree.add([''])
        return super(BazaarCommitBuilder, self).__enter__()

    def commit(self):
        tree = self.tree

        for name, content in self.contents.items():
            if not tree.path2id(name):
                tree.add([name])
            id = tree.path2id(name)
            tree.put_file_bytes_non_atomic(id, content)

        for old, new in self.renames:
            print old, '->', new
            tree.rename_one(old.lstrip('/'), new.lstrip('/'))


        self.tree.commit(
                message=self.extra['message'],
                authors=[self.author],
                timestamp=self.time_unix,
                timezone=self.time_offset,
                )

    def mkdir(self, path):
        #XXX: sanity checks?
        self.tree.mkdir(path)

    def __exit__(self, et, ev, tb):
        super(BazaarCommitBuilder, self).__exit__(et, ev, tb)
        self.tree.unlock()
        self.tree = None


class BazaarRepository(Repository):
    CommitBuilder = BazaarCommitBuilder

    #XXX: this whole thing is broken and messed
    def __init__(self, path=None, workdir=None, create=False):
        if workdir:
            assert not path and not create
            self.branch = workdir.wt.branch
        elif create:
            assert path, 'create needs a path'
            self.branch = BzrDir.create_branch_convenience(path)
        else:
            try:
                self.branch, rest = Branch.open_containing(path)
            except errors.NotBranchError:
                raise NotFoundError('bzr', path)


    def __repr__(self):
        return "<Bzr 'repo' at %s>"%self.branch.base

    def __len__(self):
        #XXX: crap
        revs = self.branch.iter_merge_sorted_revisions()

        return sum(1 for i in revs)

    def get_default_head(self):
        id = self.branch.last_revision()
        if id == "null:":
            return
        return self[id]

    def __getitem__(self, id):
        revision = self.branch.repository.get_revision(id)
        return BazaarRevision(self, revision)



    def push(self, *k, **kw):
        parent = self.branch.get_parent()
        remote = Branch.open(parent)

        self.branch.push(remote)

