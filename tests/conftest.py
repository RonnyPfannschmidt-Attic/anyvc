from .helpers import all_known, VcsMan

pytest_plugins = "doctest"

class ConftestPlugin:
    def pytest_genfuncruns(self, runspec):
        if 'mgr' not in runspec.funcargnames:
            return
        for vc in all_known:
            vcdir = runspec.config.ensuretemp(vc.__name__)
            testdir = vcdir.mkdir(runspec.function.__name__)
            runspec.addfuncarg('mgr', VcsMan(vc, testdir))

