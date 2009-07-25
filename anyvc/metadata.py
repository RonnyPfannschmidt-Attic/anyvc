"""
    anyvc.metadata
    ~~~~~~~~~~~~~~

    some basic metadata about vcs states and other fun
    
    .. warning::

      this module is subject to huge changes
"""

def _(str):
    return str #XXX: gettext

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


# known implementations
# mapping of vcs name to a listing of (type, workdir, repo)
# XXX: this format sucks, fix it


implementations = {
    'mercurial':[
        ('native', 'anyvc.workdir.hg.Mercurial', 'anyvc.repository.hg.MercurialRepository'),
        ('shell', None, None),
    ],
    'bazaar':[
        ('native', 'anyvc.workdir.bzr.Bazaar', 'anyvc.repository.bzr.BazaarRepository'),
        ('shell-xml', None, None),
        ('shell', None, None),
    ],
    'git':[
        ('dulwich', None, 'anyvc.repository.git.GitRepository'),
        ('gitpython', None, None),
        ('shell', 'anyvc.workdir.git.Git', None),
    ],
    'subversion':[
        ('subvertpy', None, 'anyvc.repository.subversion.SubversionRepository'),
        ('native', None, None),
        ('shell', 'anyvc.workdir.cmdbased.SubVersion', None),
    ],
    'darcs':[
        ('shell', None, None),
    ],
    'monotone':[
        ('shell', None, None),
    ],
}


def _import(name):
    mod, attr = name.rsplit('.', 1)
    pymod = __import__(mod, fromlist=['*'])
    return getattr(pymod, attr)

def get_wd_impl(vcs, detail):
    for name, wd, repo in implementations[vcs]:
        if name == detail:
            return wd and _import(wd)


def get_repo_impl(vcs, detail):
    for name, wd, repo in implementations[vcs]:
        if name == detail:
            return repo and _import(repo)
