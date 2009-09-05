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
                                        #remote 
        metafunc.addcall(id=name, param=(None, name))
        metafunc.addcall(id='remote/'+name, param=('python2', name))
        #XXX: later, for checking that python3 will always use a remote to python2
        # metafunc.addcall(id='python3/'+name, param=('python3', name))


def pytest_funcarg__mgr(request):
    remote, vc = request.param
    r = remote or 'local'
    vcdir = request.config.ensuretemp('%s_%s'%(vc, r) )
    testdir = vcdir.mkdir(request.function.__name__)
    return VcsMan(vc, testdir, remote)

