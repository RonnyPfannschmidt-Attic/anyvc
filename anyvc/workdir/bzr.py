#pida imports
from bases import VCSWorkDir, VCSWorkDir_WithParser
from file import StatedPath as Path


#python imports
import sys
from StringIO import StringIO

#bzr imports
from bzrlib import workingtree
from bzrlib import bzrdir
from bzrlib import osutils
from bzrlib.status import show_tree_status
from bzrlib.diff import DiffTree, _get_trees_to_diff
from bzrlib import revisionspec


class Bazaar(VCSWorkDir_WithParser):
    wt = None
    base_path = None
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
        self.setup() # really?
        self.path = path
        try:
            self.wt = workingtree.WorkingTree.open_containing(self.path)[0]
            self.base_path = self.wt.basedir
        except:
            self.base_path = ""



    def setup(self):
        #print "setup. nothing to do here now"
        pass
    
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

    def list_impl(self, paths=None, recursive=False):
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

    def parse_list_items(self, items, cache):
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
        if self.wt != None:
            try:
                added, ignored = self.wt.smart_add(paths,recursive)
                outputdata =  ("Added:\n")
                for item in added:                
                    outputdata += "  " + item + "\n"
                outputdata += ("Ignored:\n")
                for item in ignored:
                    outputdata +="  " + item + "\n"
                #should i do something with outputdata?
            except:
                print "err"
                return "Error adding %s.\n%s" % (paths, sys.exc_value)
                #dialogs._bzrErrorDialog(_("Bazaar error adding file %s") % file,sys.exc_value)
            else:
                return "Ok"

    def commit(self, paths=None, message=None, user=None):
        if self.wt != None:
            try:
                relpaths = []
                for p in paths:
                    relpaths.append(self.wt.relpath(p))
                self.wt.commit(message,author=user,specific_files=relpaths)
            except:
                return "Error commiting %s.\n%s" % (paths, sys.exc_value)
            else:
                return "Ok"

    def diff(self, paths=()):
        if self.wt != None:
            strdiff = StringIO()

            new_tree = self.wt
            old_revid = new_tree.branch.revision_history()[-2]
            old_tree = new_tree.branch.repository.revision_tree(old_revid)
            from bzrlib.diff import _get_trees_to_diff, show_diff_trees
              
            relpaths = self._get_relative_path(paths)
              
            show_diff_trees(old_tree, new_tree, strdiff,
                               specific_files=relpaths)
            return strdiff.getvalue()
                 
    def remove(self, paths=None, execute=False, recursive=False):
        if self.wt != None:
            relpaths = self._get_relative_path(paths)
            for p in paths:
                self.wt.remove(p)

    def revert(self, paths=None, missing=False):
        if self.wt != None:
            revisionid = self.wt.branch.last_revision()
            ret = self.wt.revert(old_tree=self.wt.branch.repository.revision_tree(revisionid))

    def update(self, revision=None, paths=None):
        if self.wt != None:
            self.wt.update()

    def _get_relative_path(self,paths):
        if paths is str:
            return self.wt.relpath(paths)
        else:
            relpaths = []
            for p in paths: 
                relpaths.append(self.wt.relpath(p))
            return relpaths
             
"""
To-Do
*'add'
*'commit'
*'diff'
'move'?
'pull'?
'push'?
*'remove'
'rename'?
*'revert'
'status'?
'sync'?
*'update'
"""


