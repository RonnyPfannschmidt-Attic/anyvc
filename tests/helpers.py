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
from anyvc.metadata import get_backend
from anyvc.remote import RemoteBackend

def do(*args, **kw):
    args = map(str, args)
    print args
    if 'cwd' in kw:
        kw['cwd'] = str(kw['cwd'])
    call(args, stdin=None, **kw)


class WdWrap(object):
    """wraps a vcs"""
    def __init__(self, vc, path):
        self.__path = path
        self.__vc = vc

    def __getattr__(self, name):
        return getattr(self.__vc, name)

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

    def delete_files(self, *relpaths):
        for path in relpaths:
            self.bpath(path).remove()

    def check_states(self, mapping, exact=True):
        """takes a mapping of filename-> state
        if exact is true, additional states are ignored
        returns true if all supplied files have the asumed state
        """
        __tracebackhide__ = True
        print mapping
        used = set()
        all = set()
        infos = list(self.status())
        print infos
        for info in infos:
            all.add(info.relpath)
            print info
            assert info.state in state_descriptions
            if info.relpath in mapping:
                expected = mapping[info.relpath]
                assert info.state==expected, "%s wanted %s but got %s"%(
                        info.relpath,
                        expected,
                        info.state,
                        )
                used.add(info.relpath)

        untested = set(mapping) - used

        print 'all:', sorted(all)
        print 'used:', sorted(used)
        print 'missing?:', sorted(all - used)
        print 'untested:', sorted(untested)
        assert not untested , 'not all excepted stated occured'


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

    def create_wd(self, workdir):
        path = self.bpath(workdir)
        try:
            wd = self.backend.Workdir(
                str(path),
                create=True)
            return WdWrap(wd, path)
        except: # svn (might also apply for monotone/fossil)
            repo = workdir+'-repo'
            self.make_repo(repo)
            return self.make_wd(repo, workdir)



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
