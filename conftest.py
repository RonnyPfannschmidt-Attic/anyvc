
from tests.helpers import  VcsMan

from anyvc import metadata

pytest_plugins = "doctest"

test_in_interpreters = 'python2', 'python3', 'jython', 'pypy'

test_on = {
    '%s': None,
    'remote/%s': 'popen//python=python2',
}

def pytest_addoption(parser):
    parser.addoption("--local-remoting", action="store_true", default=False)

def pytest_configure(config):
    if not config.getvalue('local_remoting'):
        for key in list(test_on):
            if '/' in key:
                del test_on[key]

def pytest_generate_tests(metafunc):
    if 'mgr' not in metafunc.funcargnames:
        return
    for name in metadata.backends:
        for id, spec in test_on.items():
            print repr(id), repr(name)
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
    backend = request.getfuncargvalue('backend')
    return VcsMan(vc, testdir, spec, backend)


def pytest_collect_directory(path, parent):
    for compiled_module in path.listdir("*.pyc"):
        if not compiled_module.new(ext=".py").check():
            compiled_module.remove()

