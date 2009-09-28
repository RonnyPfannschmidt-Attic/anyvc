from .helpers import  VcsMan

from anyvc import metadata

pytest_plugins = "doctest"


test_on = {
    '%s': None,
    'remote/%s': 'popen//python=python2',
#XXX'python3/%s': 'python3',
#XXX'jython/%s': 'jython-2.5', #XXX: slow
#XXX:'pypy/%s': 'pypy',
}


def pytest_generate_tests(metafunc):
    if 'mgr' not in metafunc.funcargnames:
        return
    for name in metadata.backends:
        for id, spec in test_on.items():
            metafunc.addcall(id=id%name, param=(name, spec))

def pytest_funcarg__backend(request):
    vc, spec = request.param
    return request.cached_setup(
            lambda: metadata.get_backend(vc, spec),
            extrakey=request.param,
            scope='session')

def pytest_funcarg__mgr(request):
    vc, spec = request.param
    r = spec or 'local'
    vcdir = request.config.ensuretemp('%s_%s'%(vc, r) )
    testdir = vcdir.mkdir(request.function.__name__)
    return VcsMan(vc, testdir, spec, request.getfuncargvalue('backend'))

