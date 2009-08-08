from .helpers import  VcsMan

from anyvc import metadata

pytest_plugins = "doctest"


def pytest_addoption(parser):
    parser.addoption( "-V", "--vcs", action="store", default=None,
        help="specify the vcs's to use")


def pytest_generate_tests(metafunc):
    names = metafunc.config.option.vcs
    if names:
        names = names.split(",")
        assert any(vc.__name__ == name for name in names for vc in all_known), "%r not known"%(names,)


    if 'mgr' not in metafunc.funcargnames:
        return
    for name in metadata.backends:
        if names and name not in names:
            continue
        metafunc.addcall(id=name, param=name)


def pytest_funcarg__mgr(request):
    vc = request.param
    vcdir = request.config.ensuretemp(vc)
    testdir = vcdir.mkdir(request.function.__name__)
    return VcsMan(vc, testdir)

