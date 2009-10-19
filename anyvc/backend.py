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
        self.__name__ = module_name
        self.module = mod = __import__(module_name, fromlist=['*'])
        self.__dict__.update(mod.__dict__)

    def __repr__(self):
        return '<anyvc backend %s>'%(self.name,)

    def _import_subclass_from(self, module, base, exclude=None):
        if exclude is None:
            exclude = (base,)

        impl_module = __import__(module, fromlist=['*'])
        for var in vars(impl_module).values():
            if (isinstance(var, type)
                and issubclass(var, base)
                and var not in exclude):
                return var
        raise ImportError(
                '%s class for %r not found'%(
                base.__name__, self.module,)
            )

    @cachedproperty
    def Repository(self):
        #XXX: a crude&nasty
        return self._import_subclass_from(
                self.module.__name__+'.repo',
                Repository
            )

    @cachedproperty
    def Workdir(self):
        return self._import_subclass_from(
                module=self.__name__+'.workdir',
                base=WorkDir,
                exclude=(WorkDir, WorkDirWithParser, CommandBased)
            )
