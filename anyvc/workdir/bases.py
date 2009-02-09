# -*- coding: utf-8 -*- 
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
"""
    weird base classes

    :copyright: 2008 Ronny Pfannschmidt
    :license: LGPL2 or later
"""
__all__ = ["VCSWorkDir",]

from .file import StatedPath
from os.path import join

class VCSWorkDir (object):
    """
    Base class for all vcs's
    remember not to use super in subclasses
    """

    def __init__(self, path): 
        self.setup()
        self.path = path

    def status(self, paths=(), recursive=True):
        """
        yield a list of Path instances tagged with status informations
        """
        raise NotImplementedError

    def diff(self, paths=()):
        raise NotImplementedError

    def update(self, revision=None):
        raise NotImplementedError

    def commit(self, paths=None, message=None, user=None):
        raise NotImplementedError

    def revert(self, paths=None, missing=False):
        raise NotImplementedError

    def add(self, paths=None, recursive=False):
        raise NotImplementedError

    def remove(self, paths=None, execute=False, recursive=False):
        raise NotImplementedError

    def rename(self, source=None, target=None):
        raise NotImplementedError

class VCSWorkDir_WithParser(VCSWorkDir):

    def parse_status_items(self, items, cache):
        """
        redirect to parse_status_item
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
