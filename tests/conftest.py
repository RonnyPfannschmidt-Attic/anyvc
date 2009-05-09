from .helpers import all_known, VcsMan


class ConftestPlugin:
    def pytest_pycollect_genfuncargs(self, function):
        if not function.hasfuncarg('mgr'):
            return
        for vc in all_known:
            testdir = function.config.ensuretemp(vc.__name__).mkdir(function.name)
            yield { 'mgr': VcsMan(vc, testdir) }

