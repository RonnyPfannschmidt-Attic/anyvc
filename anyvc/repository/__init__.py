"""
    Anyvc git repo support

    :license: LGPL 2 or later
    :copyright: 2009 by Ronny Pfannschmidt
"""

from . import hg
from . import subversion
from . import bzr
from . import git
lookup = {
    'Mercurial': hg.MercurialRepository,
    'SubVersion': subversion.SubversionRepository,
    'Bazaar': bzr.BazaarRepository,
    'Git': git.GitRepository
}

def get_repo_mgr(name):
    #XXX: make more nice later
    return lookup.get(name)
