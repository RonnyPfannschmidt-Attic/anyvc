import sys
import os

from anyvc.common.workdir import WorkDirWithParser
from ..exc import NotFoundError

from StringIO import StringIO

#bzr imports
from bzrlib.branch import Branch
from bzrlib.workingtree import WorkingTree
from bzrlib.errors import NotBranchError
from bzrlib import bzrdir
from bzrlib import osutils
from bzrlib.status import show_tree_status
from bzrlib.diff import DiffTree
from bzrlib.diff import show_diff_trees
from bzrlib import revisionspec


class Bazaar(WorkDirWithParser):
    statemap  = {
            "unknown:": 'unknown',
            "added:": 'added',
            "unchanged:": 'clean',
            "removed:": 'removed',
            "ignored:": 'ignored',
            "modified:": 'modified',
            "conflicts:": 'conflict',
            "pending merges:": 'conflict',
            "renamed:": "placeholder", # special cased, needs parsing
            #XXX: figure why None didn't work
            }

    @property
    def repository(self):
        from .repo import BazaarRepository

        return BazaarRepository(workdir=self)

    def __init__(self, path, create=False, source=None):


        self.path = path

        if create:
            assert source
            source,r = Branch.open_containing(source)
            source.bzrdir.sprout(path)

        try:
            self.wt, self._rest = WorkingTree.open_containing(self.path)
            self.base_path = self.wt.basedir
        except NotBranchError:
            raise NotFoundError(self.__class__, path)

    def status_impl(self, *k, **kw):
        #XXX: paths, recursion
        self.wt.lock_read()
        try:
            for change in self.wt.iter_changes(self.wt.basis_tree(),
                                               include_unchanged=True,
                                               want_unversioned=True,
                                               ):
                yield change
        finally:
            self.wt.unlock()

    def parse_status_item(self, change, cache):

        (file_id,
            paths, changed, versioned,
            parent, name, kind,
            executable) = change

        if file_id=='TREE_ROOT':
            return None

        #XXX: propperly handle removed vs deleted vs made untracked

        # paths -> renamed
        source, target = paths
        result_path = target if isinstance(target, unicode) else source

        # versioned add/remove
        old, new = versioned
        if new and not old:
            return 'added', result_path
        elif old and not new:
            # deleted ?!
            return 'removed', result_path
        elif not new and not old:
            return 'unknown', result_path
        elif source!=target:
            return None, paths
        elif changed:
            if kind[0] != kind[1]:
                return 'missing', result_path
            return 'modified', result_path
        elif all(versioned):
            return 'clean', result_path

        #XXX more tricky things ?!

    def add(self, paths=None, recursive=False):
        paths = self._abspaths(paths)
        try:
            added, ignored = self.wt.smart_add(paths,recursive)
            #XXX: more info?
        except:
            print "err"
            return "Error adding %s.\n%s" % (paths, sys.exc_value)
            #dialogs._bzrErrorDialog(_("Bazaar error adding file %s") % file,sys.exc_value)
        else:
            return "Ok"

    def commit(self, paths=None, message=None, user=None):
        paths = self._abspaths(paths)
        #XXX: this is weird
        if paths is not None:
            paths = map(self.wt.relpath, paths)
        self.wt.commit(message,author=user,specific_files=paths)

    def diff(self, paths=None):
        strdiff = StringIO()

        if paths is not None:
            paths = self._abspaths(paths)
            #XXX: this is weird
            paths = map(self.wt.relpath, paths)
        if paths is not None:
            show_diff_trees(self.wt.basis_tree(), self.wt, strdiff,
                            specific_files=paths)
        else:
            show_diff_trees(self.wt.basis_tree(), self.wt, strdiff)
        return strdiff.getvalue()

    def remove(self, paths=None, execute=False, recursive=False):
        assert paths is not None, 'uh wtf, dont do that till there is a sane ui'
        self.wt.remove(self._abspaths(paths), keep_files=False)

    def rename(self, source, target):
        #XXX: again the relpath weird :(
        self.wt.rename_one(
            self.wt.relpath(os.path.join(self.base_path, source)),
            self.wt.relpath(os.path.join(self.base_path, target)))

    def revert(self, paths=None, missing=False):

        revisionid = self.wt.branch.last_revision()
        ret = self.wt.revert(old_tree=self.wt.branch.repository.revision_tree(revisionid))

    def update(self, revision=None, paths=None):
        assert not revision and not paths
        #XXX fail
        self.wt.update()

    def _abspaths(self, paths):
        if paths is not None:
            return [ os.path.join(self.base_path, path) for path in paths]
"""
To-Do
*'remove'
'rename'?
*'revert'
'status'?
*'update'
"""


