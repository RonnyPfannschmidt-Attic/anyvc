# -*- coding: utf-8 -*-
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
"""
    weird base classes

    :copyright: 2008 Ronny Pfannschmidt
    :license: LGPL2 or later
"""
from os.path import join

from os.path import dirname, basename, join, normpath

class StatedPath(object):
    """
    stores status informations about files

    >>> StatedPath('a.txt')
    <normal 'a.txt'>
    >>> StatedPath('a.txt', 'changed')
    <changed 'a.txt'>

    """

    def __init__(self, name, state='normal', base=None):
        self.relpath = normpath(name)
        self.path = dirname(name)
        self.name = basename(name)
        self.base = base
        self.state = intern(state)
        if base is not None:
            self.abspath = join(base, name)
        else:
            self.abspath = None

    def __repr__(self):
        return '<%s %r>'%(
                self.state,
                self.relpath,
                )

    def __str__(self):
        return self.relpath

def find_basepath(act_path, wanted_subdir):
    detected_path = None
    detected_sd = None
    op = None
    ignored_path = os.environ.get('ANYVC_IGNORED_PATHS', '').split(os.pathsep)
    while act_path != op:
        if os.path.exists( os.path.join(act_path, wanted_subdir)):
            if act_path in ignored_path:
                return None
            detected_path = act_path
            # continue cause some vcs's
            # got the subdir in every path
        op = act_path
        act_path = os.path.dirname(act_path)
    return detected_path

class WorkDir(object):
    """
    Basic Workdir API

    :param path: base path
    :raises NotFoundError: missing the correct vcs control dir
    """

    def __init__(self, path, create=False, source=None):
        self.path = os.path.normpath( os.path.abspath(path) )
        if create:
            if source:
                self.create_from(source)
            else:
                assert create and source
        self.base_path = find_basepath(self.path, self.detect_subdir)
        if self.base_path is None:
            raise NotFoundError(self.__class__,self.path)

    def process_paths(self, paths):
        """
        process paths for vcs's usefull for "relpath-bitches"
        """
        return list(paths)

    def status(self, paths=(), recursive=True):
        """
        :param path: the filenames
        :type path: sequence of string
        :param recursive: proceed recursive for directories
        :type recursive: bool

        yield a list of Path instances tagged with status informations
        """
        raise NotImplementedError

    def diff(self, paths=()):
        """
        given a list of paths it will return a diff
        """
        raise NotImplementedError

    def update(self, paths=(), revision=None):
        """
        :param revision: the target revision
                         may not actually work for
                         vcs's with tricky workdir revision setups

        updates the workdir to either the closest head or or the given revision
        """
        raise NotImplementedError

    def commit(self, paths=(), message=None, user=None):
        """
        :param path: the paths
        :param message: the commit message
        :param user: optional author name

        commits the given paths/files with the given commit message and author
        """

        raise NotImplementedError

    def revert(self, paths=None, missing=False):
        raise NotImplementedError

    def add(self, paths=None, recursive=False):
        raise NotImplementedError

    def remove(self, paths=None, execute=False, recursive=False):
        raise NotImplementedError

    def rename(self, source=None, target=None):
        raise NotImplementedError


class WorkDirWithParser(WorkDir):

    def parse_status_items(self, items, cache):
        """
        for each `item` in `items` invoke::
        
            self.parse_status_item(item, cache)

        .. note::
            a more complex parser might need to overwrite
        """
        for item in items:
            rv = self.parse_status_item(item, cache)

            if rv is not None:
                state, name = rv
                #XXX: here renames get turned into ugly add/remove pairs
                if state is None:
                    old, new = name
                    yield StatedPath(old, 'removed', self.base_path)
                    yield StatedPath(new, 'added', self.base_path)
                else:
                    yield StatedPath(name, state, self.base_path)


    def parse_status_item(self, item, cache):
        """
        parse a single status item
        meant to be overridden
        """
        raise NotImplementedError

    def parse_cache_items(self, items):
        """
        parses vcs specific cache items to a list of (name, state) tuples
        """
        return []

    def cache_impl(self, paths=False, recursive=False):
        """
        creates a list of vcs specific cache items
        only necessary by messed up vcs's

        in case of doubt - dont touch ^^
        """
        return []

    def status_impl(self, paths=False, recursive=False):
        """
        yield a list of vcs specific listing items
        """
        raise NotImplementedError

    def cache(self, paths=(), recursive=False):
        """
        return a mapping of name to cached states
        only necessary for messed up vcs's
        """
        return dict(
                self.parse_cache_items(
                self.cache_impl(
                    paths = paths,
                    recursive=recursive
                    )))

    def status(self, paths=(), recursive=True):
        """
        yield a list of Path instances tagged with status informations
        """
        cache = self.cache(paths = paths,recursive=recursive)
        return self.parse_status_items(
                self.status_impl(
                    paths = paths,
                    recursive=recursive,
                    ), cache)


import re

from subprocess import Popen, PIPE, STDOUT, call
import os, os.path

#TODO: more reviews

from ..exc import NotFoundError

def relative_to(base_path):
    """
    will turn absolute paths to paths relative to the base_path

    .. warning:
        will only work on paths below the base_path
        other paths will be unchanged
    """
    base_path = os.path.normpath(base_path)
    l = len(base_path)
    def process_path(path):

        if path.startswith(base_path):
            return "." + path[l:]
        else:
            return path
    return process_path


class CommandBased(WorkDirWithParser):
    """
    Base class for all command based rcs's
    """
    #TODO: set up the missing actions





    def execute_command(self, args, result_type=str, **kw):
        if not args:
            raise ValueError('need a valid command')
        ret = Popen(
                [self.cmd] + args,
                stdout=PIPE,
                stderr=STDOUT,
                cwd=self.base_path,
                close_fds=True,
                env=dict(os.environ, LANG='C',LANGUAGE='C', LC_All='C'),
                )
        if result_type is str:
            return ret.communicate()[0]
        elif result_type is iter:
            return ret.stdout
        elif result_type is file:
            return ret.stdout

    def get_commit_args(self, message, paths=(), **kw):
        """
        creates a argument list for commiting

        :param message: the commit message
        :param paths: the paths to commit
        """
        return ['commit','-m', message] + self.process_paths(paths)

    def get_diff_args(self, paths=(), **kw):
        return ['diff'] + self.process_paths(paths)

    def get_update_args(self, revision=None, **kw):
        if revision:
            return ['update', '-r', revision]
        else:
            return ['update']

    def get_add_args(self, paths=(), recursive=False, **kw):
        return ['add'] + self.process_paths(paths)

    def get_remove_args(self, paths=(), recursive=False, execute=False, **kw):
        return ['remove'] +  self.process_paths(paths)

    def get_revert_args(self, paths=(), recursive=False, **kw):
        return ['revert'] + self.process_paths(paths)

    def get_status_args(self,**kw):
        raise NotImplementedError("%s doesn't implement status"%self.__class__.__name__)

    def commit(self, **kw):
        args = self.get_commit_args(**kw)
        return self.execute_command(args, **kw)

    def diff(self, **kw):
        args = self.get_diff_args(**kw)
        return self.execute_command(args, **kw)

    def update(self, **kw):
        args = self.get_update_args(**kw)
        return self.execute_command(args, **kw)

    def add(self, **kw):
        args = self.get_add_args(**kw)
        return self.execute_command(args, **kw)

    def remove(self, **kw):
        args = self.get_remove_args(**kw)
        return self.execute_command(args, **kw)

    def rename(self, source, target, **kw):
        args = self.get_rename_args(source, target)
        return self.execute_command(args, **kw)

    def revert(self, **kw):
        args = self.get_revert_args(**kw)
        return self.execute_command(args, **kw)

    def status_impl(self, **kw):
        """
        the default implementation is only cappable of
        recursive operation on the complete workdir

        rcs-specific implementations might support
        non-recursive and path-specific listing
        """
        args = self.get_status_args(**kw)
        return self.execute_command(args, result_type=iter, **kw)

    def cache_impl(self, recursive, **kw):
        """
        only runs caching if it knows, how
        """
        args = self.get_cache_args(**kw)
        if args:
            return self.execute_command(args, result_type=iter, **kw)
        else:
            return []

    def get_cache_args(self, **kw):
        return None





