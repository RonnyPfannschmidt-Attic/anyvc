#pida imports
from bases import VCSWorkDir, VCSWorkDir_WithParser
from file import StatedPath as Path


#python imports
import sys
from StringIO import StringIO

#bzr imports
import os
from bzrlib.workingtree import WorkingTree
from bzrlib.errors import NotBranchError
from bzrlib import bzrdir
from bzrlib import osutils
from bzrlib.status import show_tree_status
from bzrlib.diff import DiffTree, _get_trees_to_diff
from bzrlib import revisionspec


class Bazaar(VCSWorkDir_WithParser):
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

    def __init__(self,path): 
        self.path = path
        try:
            self.wt, self._rest = WorkingTree.open_containing(self.path)
            self.base_path = self.wt.basedir
        except NotBranchError:
            raise ValueError("no Bazaar repo below "+path)

    def cache_impl(self, paths=False, recursive=False):
        if self.wt == None:
            return []
        tree = self.wt
        outf = StringIO()
        show_tree_status(tree, show_ids=False,
                         specific_files=None, revision=None,
                         to_file=outf, short=False, versioned=False,
                         show_pending=True)
        return outf.getvalue().split("\n")

    def parse_cache_items(self, items):
        state = 'none'
        for item in items:
            item = item.rstrip()
            state = self.statemap.get(item.rstrip(), state)
            if item.startswith("  ") and state:
                if state == "placeholder":
                    old, new = item.split(" => ")
                    old, new = old.strip(), new.strip()
                    yield old, 'removed'
                    yield new, 'added'
                else:
                    yield item.strip(), state

    def status_impl(self, paths=None, recursive=False):
        if self.wt == None:
            return []
        fulllist = []
        for path in paths:
            try:
                tree, branch, relpath = bzrdir.BzrDir.open_containing_tree_or_branch(
                path)
            except:
                continue
            tree.lock_read()
            prefix = relpath 
            try:
                for fp, fc, fkind, fid, entry in tree.list_files():

                    if fp.startswith(relpath):
                        fp = osutils.pathjoin(prefix, fp[len(relpath):])
                        if fp[0] == "/":
                            fp = fp[1:]
                        if not recursive and '/' in fp:
                            continue
                        kindch = entry.kind_character()
                        outstring = '%-8s %s%s' % (fc, fp, kindch)
                        fulllist.append(outstring)
            except:
                print "anyvc-bzr:err?"
            finally:
                tree.unlock()

        return fulllist

    def parse_status_items(self, items, cache):
        if self.base_path != None:
            relpath =  self.path[len(self.base_path):]

            if relpath != '' and relpath[0] == '/':
                relpath = relpath[1:]
            for item in items:
                if not item:
                    continue
                fn = item[1:].strip()
                if relpath != '':
                    fullfn = relpath+"/"+fn
                else:
                    fullfn = fn

                if item.startswith('I'):
                    yield Path(fullfn, 'ignored', self.base_path)
                else:
                    x = Path(
                            fullfn,
                            cache.get(fullfn, 'clean'),
                            self.base_path)
                    yield x
    
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
        try:
            paths = self._abspaths(paths)
            self.wt.commit(message,author=user,specific_files=paths)
        except:
            #XXX: better handling
            return "Error commiting %s.\n%s" % (paths, sys.exc_value)
        else:
            #XXX: better output
            return "Ok"

    def diff(self, paths=None):
        strdiff = StringIO()

        from bzrlib.diff import show_diff_trees
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
        self.wt.remove(self._abspaths(paths))

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
*'commit'
*'diff'
*'remove'
'rename'?
*'revert'
'status'?
*'update'
"""


