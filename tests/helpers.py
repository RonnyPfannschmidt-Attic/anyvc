# copyright 2008 by Ronny Pfannschmidt
# license lgpl3 or later

from __future__ import with_statement
import os
import sys 

from anyvc.workdir import all_known
from functools import wraps, partial
from os.path import join, dirname, exists
from tempfile import mkdtemp
from subprocess import Popen, PIPE
from shutil import rmtree
from nose.tools import assert_equal


def do(*args, **kw):
    print args
    p = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE, **kw)
    sys.stdout.write(p.stdout.read())
    sys.stdout.write(p.stderr.read())


def disable(func):
    return None

def for_all(func):

    @wraps(func)
    def single(vc):
        with VcsMan(vc) as man:
            func(man)

    @wraps(func)
    def test():
        for vc in all_known:
            yield single, vc
    return test

def generic(func):
    """this is a dirty little dispatcher, 
    its in place cause most stuff only half works"""

    @wraps(func)
    def wrap(self, *k, **kw):
        spec = '%s_%s'%(func.__name__, self.vc.__name__.lower())
        call = getattr(self, spec, None)
        if call is None:
            call = getattr(self, func.__name__ + '_generic', None)
            assert call is not None, 'cant find function %s for %r'%(
                    func.__name__, 
                    self.vc.__name__,
                    )
        return func(self, call, *k, **kw)
    return wrap

class WdWrap(object):
    """wraps a vcs"""
    def __init__(self, vc, path):
        self.__path = path
        self.__vc = vc(path)

    def __getattr__(self, key):
        return getattr(self.__vc, key)

    def bpath(self, name):
        return join(self.__path, name)

    def put_files(self, mapping):
        for name, content in mapping.items():
            path = self.bpath(name)
            dir = dirname(path)
            if not exists(dir):
                os.makedirs(dir)
            with open(path, 'w') as f:
                f.write(content)

    def check_states(self, mapping, exact=False):
        """takes a mapping of filename-> state
        if exact is true, additional states are ignored
        returns true if all supplied files have the asumed state
        """
        print mapping
        used = set()
        infos = list(self.status())
        for info in infos:
            print repr(info)
            if info.relpath in mapping:
                assert info.state==mapping[info.relpath], info.path
                used.add(info.relpath)

        if exact:
            assert len(mapping) == len(used), 'not all excepted stated occured'




class VcsMan(object):
    """controller over a tempdir for tests"""
    def __init__(self, vc):
        self.vc = vc
        self.base = mkdtemp()

    def bpath(self, name):
        return join(self.base, name)

    def __enter__(self):
        return self

    def __exit__(self, type, value, args):
        if type is None:
            rmtree(self.base)
            return True
        else:
            print self.base
            return False

    @generic #XXX:lazy hack, completely missplaced
    def make_wd(self, spec, repo, workdir):
        """this one is weird, checkout for normal vcs's, clone for dvcs's"""
        spec(self.bpath(repo), self.bpath(workdir))
        return WdWrap(self.vc, self.bpath(workdir))

    def make_wd_mercurial(self, repo, workdir):
        do('hg', 'clone', repo, workdir)

    make_wd_nativemercurial = make_wd_mercurial


    def make_wd_bazaar(self, repo, workdir):
        do('bzr', 'branch', repo, workdir)

    def make_wd_subversion(self, repo, workdir):
        do('svn', 'co', 'file://'+repo, workdir)

    def make_wd_git(self, repo, workdir):
        do('git', 'clone', repo, workdir)

    def make_wd_darcs(self, repo, workdir):
        do('darcs', 'get', repo, workdir)
        with open(join(workdir, '_darcs/prefs/author'), 'w') as f:
            f.write('test')

    @generic #XXX:lazy hack, completely missplaced
    def make_repo(self, spec, path):
        spec(self.bpath(path))

    def make_repo_generic(self, path):
        #XXX: return value?!
        self.vc.make_repo(path)

    def make_repo_subversion(self, path):
        do('svnadmin', 'create', path)

    def make_repo_bazaar(self, path):
        do('bzr', 'init', path)

    def make_repo_git(self, path):
        os.mkdir(path)
        do('git','init', cwd=path)
        #XXX: git doesnt like clone of empty repos
        do('git', 'commit', '--allow-empty' , '-m', 'dummy 1', cwd=path)

    def make_repo_darcs(self, path):
        os.mkdir(path)
        do('darcs', 'initialize', '--darcs-2', cwd=path)
