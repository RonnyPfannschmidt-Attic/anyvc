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
from subprocess import call
from shutil import rmtree
from nose.tools import assert_equal
from anyvc.metadata import get_backend
from anyvc.remote import RemoteBackend

def do(*args, **kw):
    args = map(str, args)
    print args
    if 'cwd' in kw:
        kw['cwd'] = str(kw['cwd'])
    call(args, stdin=None, **kw)


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
        spec = '%s_%s'%(func.__name__, self.vc)
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
        self.__vc = vc

    def __getattr__(self, key):
        return getattr(self.__vc, key)

    def bpath(self, name):
        return self.__path.join(name)

    def put_files(self, mapping):
        for name, content in mapping.items():
            path = self.__path.ensure(name)
            path.write(content.rstrip() + '\n')

    def has_files(self, *files):
        missing = [name for name in map(self.bpath, files) if not name.check()]
        assert not missing, 'missing %s'%', '.join(missing)
        return not missing

    def delete_files(self, *files):
        for file in files:
            self.bpath(file).remove()

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
    def __init__(self, vc, base, xspec, backend):
        self.remote = xspec is not None
        self.vc = vc
        self.base = base.ensure(dir=True)
        self.xspec = xspec
        self.backend = backend

    def __repr__(self): 
        return '<VcsMan %(vc)s %(base)r>'%vars(self)

    def bpath(self, name):
        return self.base.join(name)

    def make_wd(self, repo, workdir):
        path = self.bpath(workdir)
        wd = self.backend.Workdir(
                str(path),
                create=True,
                source=str(self.bpath(repo)))

        return WdWrap(wd, path)

    def make_repo(self, path):
        return self.backend.Repository(
                path=str(self.bpath(path)),
                create=True)

    def make_wd_darcs(self, repo, workdir):
        do('darcs', 'get', repo, workdir)
        workdir.join('_darcs/prefs/author').write('test')

    def make_repo_darcs(self, path):
        path.ensure(dir=True)
        do('darcs', 'initialize', '--darcs-2', cwd=path)
