"""
    Anyvc Backend loading abstraction

    '

    :license: LGPL2
    :copyright: 2009 by Ronny Pfannschmidt
"""

from anyvc.util import cachedproperty
from anyvc.common.repository import Repository
from anyvc.common.workdir import WorkDir, WorkDirWithParser, CommandBased

class Backend(object):
    def __init__(self, name, module_name):
        self.name = name
        self.module_name = module_name

    def __repr__(self):
        return '<anyvc backend %s>'%(self.name,)

    def _import(self, name):
        module, attr = name.split(':')
        try:
            impl_module = __import__(module, fromlist=['*'])
            return getattr(impl_module, attr)
        except (ImportError, AttributeError):
            raise ImportError(name)

    def is_workdir(self, path):
        return self.module.is_workdir(path)

    def is_repository(self, path):
        return self.module.is_repository(path)

    @cachedproperty
    def module(self):
        return __import__(self.module_name, fromlist=['*'])

    @cachedproperty
    def features(self):
        return set(self.module.features)

    @cachedproperty
    def Repository(self):
        return self._import(self.module.repo_class)

    @cachedproperty
    def Workdir(self):
        return self._import(self.module.workdir_class)
