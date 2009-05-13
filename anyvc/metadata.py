"""
    anyvc.metadata
    ~~~~~~~~~~~~~~

    some basic metadata about vcs states and other fun
"""

def _(str): return str #XXX: gettext

state_descriptions = dict(
    #XXX: finish, validate
    unknown = _("not known to the vcs"),
    ignored = _("ignored by the vcs"),
    added = _("added"),
    clean = _("known by the vcs and unchanged"),
    modified =_("changed in the workdir"),
    missing = _("removed from the workdir, still recorded"),
    removed = _("removed by deletion or renaming"),
    conflicte = _("merge conflict")
)

aliases = {
    'svn': 'subversion',
    'bzr': 'bazaar',
    'hg': 'mercurial',
    'mtn': 'monotone',
}


implementations = {
    'mercurial':{
        'native': None,
        'shell': None
        },
    'bzr':{
        'native': None,
        'shell': None,
        'shell-xml':None
        },
    'git':{
        'shell': None,
        'dulwich': None,
        'gitpython': None,
        },
    'subversion':{
        'native': None,
        'shell': None,
        'subvertpy': None,
        },
    'darcs':{
        'shell': None,
        },
    'monotone':{
        'shell': None
        },
}

preferences = {
    'mercurial': 'native shell'.split(),
    'bazaar': 'native shell-xml shell'.split(),
    'subversion': 'subvertpy native shell'.split(),
}
