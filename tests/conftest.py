from .helpers import all_known, VcsMan

pytest_plugins = "doctest"

class ConftestPlugin:

    def pytest_addoption(self, parser):
        parser.addoption( "-V", "--vcs", action="store", default=None,
            help="specify the vcs's to use")


    def pytest_generate_tests(self, metafunc):
        names = metafunc.config.option.vcs
        if names:
            names = names.split(",")

        if 'mgr' not in metafunc.funcargnames:
            return
        for vc in all_known:
            if names and vc.__name not in names:
                continue
            metafunc.addcall(id=vc, param=vc)

    def pytest_funcarg__mgr(self, request):
        vc = request.param
        vcdir = request.config.ensuretemp(vc.__name__)
        testdir = vcdir.mkdir(request.function.__name__)
        return VcsMan(vc, testdir)

