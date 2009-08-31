from anyvc.metadata import get_backend


from anyvc.remote.object import RemoteHandler

def start_controller(channel):
    backend_module = channel.receive()
    try:
        backend = __import__(backend_module, fromlist=['*'])
    except ImportError:
        channel.send(None) # magic value for 'i dont have it'
        return

    workchan = channel.gateway.newchannel()
    SlaveBackend(workchan, backend)
    channel.send(workchan)


class SlaveBackend(RemoteHandler):
    def __init__(self, channel, backend):
        RemoteHandler.__init__(self, channel)
        self.backend = backend


    def open_repo(self, *k,**kw):
        repo = self.backend.Repository(*k, **kw)
        channel = self.newchannel()
        RepositoryHandler(channel, repo)
        return channel

    def open_workdir(self, *k, **kw):
        workdir = self.backend.Workdir(*k, **kw)
        channel = self.newchannel()
        WorkdirHandler(channel, workdir)
        return channel


class RepositoryHandler(RemoteHandler):
    def __init__(self, channel, repo):
        RemoteHandler.__init__(self, channel)
        self.repo = repo

    def push(self):
        self.repo.push()

    def get_default_head(self):
        return self.repo.get_default_head().id

    def commit_message(self, id):
        return self.repo[id].message

    def commit_diff(self, id):
        return self.repo[id].get_parent_diff()

    def commit_file_content(self, id, path):
        try:
            return self.repo[id].file_content(path)
        except IOError:
            return None

    def commit_parents(self, id):
        return [p.id for p in self.repo[id].parents]

    def commit_time(self, id):
        return self.repo[id].time

    def commit_author(self, id):
        return self.repo[id].author

    def prepare_default_structure(self):
        self.repo.prepare_default_structure()

    def count_revisions(self):
        return len(self.repo)

    def transaction(self, **kw):
        transaction = self.repo.transaction(**kw)
        channel = self.newchannel()
        TransactionHandler(channel, transaction, self.repo)
        return channel


class WorkdirHandler(RemoteHandler):
    def __init__(self, channel, workdir):
        RemoteHandler.__init__(self, channel)
        self.workdir = workdir

    def path(self):
        return self.workdir.path

    def add(self, **kw):
        return self.workdir.add(**kw)

    def status(self, **kw):
        return [(item.relpath, item.base, item.state)
                for item in self.workdir.status(**kw)]

    def commit(self, **kw):
        return self.workdir.commit(**kw)

    def diff(self, **kw):
        return self.workdir.diff(**kw)

    def remove(self, **kw):
        return self.workdir.remove(**kw)

    def revert(self, **kw):
        return self.workdir.revert(**kw)

    def rename(self, **kw):
        return self.workdir.rename(**kw)

    def get_local_repo(self):
        #XXX: this one shouldnt be
        repo = self.workdir.repository
        if repo is not None:
            channel = self.newchannel()
            RepositoryHandler(channel, repo)
            return channel


class TransactionHandler(RemoteHandler):
    def __init__(self, channel, transaction, repo):
        RemoteHandler.__init__(self, channel)
        self.transaction = transaction
        self.repo = repo
        self.transaction.__enter__()

    def write_file(self, path, data):
        fb = self.transaction.create(path)
        fb.seek(0)
        fb.write(data)
        fb.seek(0)

    def commit(self):
        self.transaction.__exit__(None, None, None)

    def rename(self, source, dest):
        self.transaction.rename(source, dest)

