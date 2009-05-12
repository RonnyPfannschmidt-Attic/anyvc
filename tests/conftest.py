from .helpers import all_known, VcsMan

pytest_plugins = "doctest"

class ConftestPlugin:
    def pytest_genfunc(self, funcspec):
        if 'mgr' not in funcspec.funcargnames:
            return
        for vc in all_known:
            vcdir = funcspec.config.ensuretemp(vc.__name__)
            testdir = vcdir.mkdir(funcspec.function.__name__)
            funcspec.addcall(mgr=VcsMan(vc, testdir))

