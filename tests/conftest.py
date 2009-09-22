from .helpers import  VcsMan

from anyvc import metadata

pytest_plugins = "doctest"


test_on = {
    '%s': None,
#XXX'remote/%s': 'python2',
#XXX'python3/%s': 'python3',
#XXX'jython/%s': 'jython-2.5', #XXX: slow
#XXX:'pypy/%s': 'pypy',
}


def pytest_generate_tests(metafunc):
    if 'mgr' not in metafunc.funcargnames:
        return
    for name in metadata.backends:
        for id, python in test_on.items():
            metafunc.addcall(id=id%name, param=(python, name))


def pytest_funcarg__mgr(request):
    remote, vc = request.param
    r = remote or 'local'
    vcdir = request.config.ensuretemp('%s_%s'%(vc, r) )
    testdir = vcdir.mkdir(request.function.__name__)
    return VcsMan(vc, testdir, remote)

