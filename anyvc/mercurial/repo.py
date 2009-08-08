"""
    Anyvc Mercurial repository support
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: LGPl 2 or later
    :copyright:
        * 2008 by Ronny Pfannschmidt <Ronny.Pfannschmidt@gmx.de>
"""

from ..repository.base import Repository, Revision, CommitBuilder, join
from .workdir import grab_output

from mercurial import commands, localrepo, ui, context


class MercurialRevision(Revision):
    def __init__(self, repo, rev):
        self.repo, self.rev = repo, rev

    @property
    def parents(self):
        print self.rev.parents()
        return [MercurialRevision(self.repo, rev) for rev in self.rev.parents() if rev]


    @property
    def message(self):
        return self.rev.description()

    def file_content(self, path):
        return self.rev[path].data()


class MercurialRepository(Repository):
    def __init__(self, workdir=None, path=None, create=False):
        self.path = path
        self.workdir = workdir
        #XXX: path only handling
        if workdir is not None:
            self.repo = workdir.repo
            self.ui = self.repo.ui

        elif path is not None:
            repo = localrepo.localrepository(ui.ui(), path, create=create)
            self.ui = repo.ui
            self.repo = repo

    def invalidate_cache(self):
        self.repo.invalidate()

    @grab_output
    def push(self, dest=None, rev=None):
        self.invalidate_cache()
        commands.push(self.ui, self.repo, dest, rev=rev)

    @grab_output
    def pull(self, source="default", rev=None):
        self.invalidate_cache()
        commands.pull(self.ui, self.repo, source, rev=rev)

    def __len__(self):
        return len(self.repo)

    def get_default_head(self):
        self.invalidate_cache()
        return MercurialRevision(self, self.repo['tip'])


    def transaction(self, **extra):
        return MercurialCommitBuilder(self, self.get_default_head(), **extra)


class MercurialCommitBuilder(CommitBuilder):
    def commit(self):
        repo = self.repo.repo
        def get_file(repo, ctx, path):
            #XXX: copy sources
            #XXX: renames
            #XXX: deletes
            if path in rn and path not in self.files:
                raise IOError()
            if path in rrn:
                assert base is not None
                parent = self.base_commit.rev[rrn[path]]
                if path in self.files:
                    data = self.files[path].getvalue()
                else:
                    data = parent.data()
                copyed = rrn[path]
            else:
                data = self.files[path].getvalue()
                copyed = False

            islink = False #XXX
            isexec = False #XXX


            return context.memfilectx(path, data, islink, isexec, copyed)

        rn = dict(self.renames)
        rrn = dict(reversed(x) for x in self.renames)
        #XXX: directory renames

        files = set(self.files)
        files.update(rn.keys())
        files.update(rn.values())

        if self.base_commit is not None:
            base = self.base_commit.rev.node()
        else:
            base = None
        ctx = context.memctx(
                repo,
                [base, None],
                self.extra['message'],
                sorted(files),
                get_file)
        repo.commitctx(ctx)



