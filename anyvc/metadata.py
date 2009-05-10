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
)

