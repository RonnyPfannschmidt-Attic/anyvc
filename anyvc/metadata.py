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
}


# known implementations

backends = {
    'mercurial': 'anyvc.mercurial',
    'bazaar': 'anyvc.bazaar',
    'git': 'anyvc.git',
    'subversion': 'anyvc.subversion'
}

def get_backends(use=backends):
    """
    a generator over all known backends
    """
    for backend in use:
        try:
            yield get_backend(backend)
        except ImportError:
            pass


def get_backend(vcs, use_remote=False):
    module = backends[vcs]
    if use_remote is True:
        use_remote = 'popen'
    if use_remote:
        from anyvc.remote import RemoteBackend
        return RemoteBackend(vcs, module, use_remote)
    else:
        from anyvc.backend import Backend
        return Backend(vcs, module)

def get_wd_impl(vcs):
    return get_backend(vcs).Workdir


def get_repo_impl(vcs):
    return get_backend(vcs).Repository
