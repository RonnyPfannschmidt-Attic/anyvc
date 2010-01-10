import os

from anyvc.common.workdir import CommandBased, relative_to, WorkDirWithParser
from subprocess import call
from subvertpy import client, wc, ra

from subvertpy.ra import RemoteAccess, Auth, get_username_provider, SubversionException

class SubVersionC(CommandBased):
    #XXX: disabled
    cmd = "svn"
    detect_subdir = ".svn/props"
    repository = None # no local repo

    def get_status_args(self, recursive, paths, **kw):
        #TODO: figure a good way to deal with changes in external
        # (maybe use the svn python api to do that)
        ret = ["st", "--no-ignore", "--ignore-externals", "--verbose"]
        if not recursive:
            ret.append("--non-recursive")
        return ret + list(paths)


    def create_from(self, source):
        call(['svn', 'co', 'file://'+source, self.path])

    state_map = {
            "?": 'unknown',
            "A": 'added',
            " ": 'clean',
            "!": 'missing',
            "I": 'ignored',
            "M": 'modified',
            "D": 'removed',
            "C": 'conflict',
            'X': 'clean',
            'R': 'modified',
            '~': 'clean',
            }

    def get_add_args(self, paths, **kw):
        # svn add doesnt add parent dirs by default
        return ['add', '--parents'] + paths

    def get_diff_args(self, paths=(), **kw):
        return ['diff', '--diff-cmd', 'diff'] + list(paths)

    def get_rename_args(self, source, target):
        return ['move', source, target]

    def parse_status_item(self, item, cache):
        if item[0:4] == 'svn:':
            # ignore all svn error messages
            return None
        state = item[0]
        file = item.split()[-1]
        if file == '.':
            # this is the path of the repo
            # normalize to ''
            file = ''
        #TODO: handle paths with whitespace if ppl fall in that one
        return self.state_map[state], file

class Subversion(WorkDirWithParser):
    detect_subdir= '.svn/props'
    repository = None # no local repo

    def create_from(self, source):
        #XXX: omg what a fucked up mess
        r = ra.RemoteAccess('file://' + source)
        rev = r.get_latest_revnum()
        print rev
        import os
        #XXX: wth are we doing here
        os.mkdir(self.path)
        c = client.Client(auth=Auth([get_username_provider()]))
        c.checkout('file://' + source, self.path, rev)

    def add(self, paths=None, recursive=False):
        #XXX: recursive
        import os
        #XXX: hacl
        print paths
        w = wc.WorkingCopy(
                path=self.path,
                write_lock=True,
                associated=None)
        for path in paths:
            path = os.path.join(self.path, path)
            w.add(path=path)
        w.close()

    def commit(self, paths=None, message=None, user=None):
        if paths:
            targets = [os.path.join(self.path, path) for path in paths]
        else:
            targets = [self.path]
        c = client.Client(auth=Auth([get_username_provider()]))

        def m(items):
            return message #XXX: encoding
        c.commit(targets=targets, recurse=True)

    def diff(self, *k, **kw):
        #XXX bad hack
        #XXX i was too lazy here
        return SubVersionC(self.base_path).diff(*k, **kw)

    def status_impl(self,paths=(), recursive=True):
        #XXX:recurse!!!
        w = wc.WorkingCopy(None, self.path)
        e = w.entries_read(True)
        print e.keys()
        for name, entry in e.items():
            if not name: #ignore root for now
                continue 
            yield name, entry
        others = os.listdir(self.path)
        for item in others:
            if item=='.svn':
                continue
            print item
            yield item, None #unknown

    def parse_status_item(self, item, cache):
        name, e = item
        if e is None:
            return 'unknown', name
        print e.kind, e.schedule, repr(e.name)
        map = {
            wc.SCHEDULE_ADD: 'added',
            wc.SCHEDULE_DELETE: 'removed',
            wc.SCHEDULE_NORMAL: 'normal',
        }
        full_path = os.path.join(self.base_path, name)
        if not os.path.exists(full_path):
            return 'missing', name
        return map[e.schedule], name
