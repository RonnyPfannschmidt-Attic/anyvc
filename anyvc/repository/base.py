"""
    Anyvc Repository Base Classes
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Various base classes for dealing with history data

    :license: LGPl 2 or later
    :copyright:
        * 2008 by Ronny Pfannschmidt <Ronny.Pfannschmidt@gmx.de>

    .. warning::

        the repo apis are unstable and incomplete

"""

class Repository(object):
    """
    represents a repository
    """

    local = True

    def __init__(self,**extra):
        self.path = path
        self.extra = extra

    def push(self, dest=None, rev=None):
        """
        push to a location

        :param dest: the destination 
        :param rev: the maximum revision to push, may be none for latest
        """
        raise NotImplementedError("%r doesnt implement push"%self.__class__)

    def pull(self, source=None, rev=None):
        """
        counterpart to push
        """
        raise NotImplementedError("%r doesnt implement pull"%self.__class__)
