
from anyvc.workdir.cmdbased import CommandBased, relative_to
from subprocess import call

class SubVersion(CommandBased):
    cmd = "svn"
    detect_subdir = ".svn"
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
