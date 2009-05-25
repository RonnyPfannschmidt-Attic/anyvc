# copyright 2008 by Ronny Pfannschmidt
# license lgpl3 or later

from __future__ import with_statement
import os
import sys 

from anyvc.workdir import all_known
from anyvc.metadata import state_descriptions
from functools import wraps, partial
from os.path import join, dirname, exists
from tempfile import mkdtemp
from subprocess import Popen, PIPE
from shutil import rmtree
from nose.tools import assert_equal
from anyvc.repository import get_repo_mgr

def do(*args, **kw):
    args = map(str, args)
    print args
    if 'cwd' in kw:
        kw['cwd'] = str(kw['cwd'])
    p = Popen(args, stdin=None, stdout=PIPE, stderr=PIPE, **kw)
    for out in p.communicate():
        sys.stdout.write(out)


def for_all(func):
    return func

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
        self.__vc = vc(str(path))

    def __getattr__(self, key):
        return getattr(self.__vc, key)

    def bpath(self, name):
        return self.__path.join(name)

    def put_files(self, mapping):
        for name, content in mapping.items():
            path = self.__path.ensure(name)
            path.write(content.rstrip() + '\n')

    def has_files(self, *files):
        for name in files:
            path = self.bpath(name)
            assert os.path.exists(str(path))
        return True
    
    def delete_files(self, *files):
        for file in files:
            os.unlink(str(self.bpath(file)))

    def check_states(self, mapping, exact=True):
        """takes a mapping of filename-> state
        if exact is true, additional states are ignored
        returns true if all supplied files have the asumed state
        """
        print mapping
        used = set()
        all = set()
        infos = list(self.status())
        for info in infos:
            all.add(info.relpath)
            assert info.state in state_descriptions
            if info.relpath in mapping:
                expected = mapping[info.relpath]
                assert info.state==expected, "%s %s<>%s"%(
                        info.relpath, 
                        info.state,
                        expected,
                        )
                used.add(info.relpath)
        

        if exact:
            print infos
            print 'all:', all
            print 'used:', used
            print 'missing?:', all - used
            assert len(mapping) == len(used), 'not all excepted stated occured'




class VcsMan(object):
    """controller over a tempdir for tests"""
    def __init__(self, vc, base):
        self.vc = vc
        self.base = base

    def bpath(self, name):
        return self.base.join(name)

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
        do('svn', 'co', 'file://%s'%repo, workdir)

    def make_wd_git(self, repo, workdir):
        do('git', 'clone', repo, workdir)

    def make_wd_darcs(self, repo, workdir):
        do('darcs', 'get', repo, workdir)
        workdir.join('_darcs/prefs/author').write('test')

    @generic #XXX:lazy hack, completely missplaced
    def make_repo(self, spec, path):
        return spec(self.bpath(path))

    def make_repo_generic(self, path):
        #XXX: return value?!
        VCM = get_repo_mgr(self.vc.__name__)
        return VCM(path=str(path), create=True)

    def make_repo_darcs(self, path):
        path.ensure(dir=True)
        do('darcs', 'initialize', '--darcs-2', cwd=path)
