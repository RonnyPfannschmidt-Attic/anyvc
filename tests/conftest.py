import py
from tests.helpers import  VcsMan

from anyvc import metadata

pytest_plugins = "doctest"

test_in_interpreters = 'python2', 'python3', 'jython', 'pypy'

test_on = {
    '%s': None,
    'remote/%s': 'popen//python=python2',
}

def pytest_addoption(parser):
    g = parser.getgroup('anyvc')
    g.addoption("--local-remoting", action="store_true", default=False,
               help='test via execnet remoting')
    g.addoption("--no-direct-api", action="store_true", default=False,
                help='don\'t test the direct api')
    g.addoption("--vcs", action='store', default=None)

def pytest_configure(config):
    if not config.getvalue('local_remoting'):
        for key in list(test_on):
            if '/' in key:
                del test_on[key]
    if config.getvalue('no_direct_api'):
        for key in list(test_on):
            if '/' not in key:
                del test_on[key]

    assert test_on,  'you shouldnt disable all test variations'

    vcs = config.getvalue('vcs')
    vcs = vcs.split('-')[0]
    if vcs is None:
        return
    if vcs not in metadata.backends:
        if vcs in metadata.aliases:
            vcs = metadata.aliases[vcs]
            config.option.vcs = vcs
        else:
            raise KeyError(vcs, '%r not found' % vcs)


funcarg_names = set('mgr repo wd backend'.split())

def pytest_generate_tests(metafunc):
    if not funcarg_names.intersection(metafunc.funcargnames):
        return
    for name in metadata.backends:
        wanted = metafunc.config.getvalue('vcs')
        if wanted is not None and name!=wanted:
            continue
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
    backend = request.getfuncargvalue('backend')

    required_features = getattr(request.function, 'feature', None)
    
    if required_features:
        required_features = set(required_features.args)
        difference = required_features.difference(backend.features)
        print required_features
        if difference:
            py.test.skip('%s lacks features %r' % (vc, sorted(difference)))

    return VcsMan(vc, testdir, spec, backend)

def pytest_funcarg__repo(request):
    return request.getfuncargvalue('mgr').make_repo('repo')

def pytest_funcarg__wd(request):
    mgr = request.getfuncargvalue('mgr')
    if 'wd:heavy' not in mgr.backend.features:
        repo = request.getfuncargvalue('repo')
        wd = mgr.create_wd('wd', repo)
    else:
        wd = mgr.create_wd('wd')

    if hasattr(request.function, 'files'):
        files = request.function.files.args[0]
        wd.put_files(files)
        assert wd.has_files(*files)
        if  hasattr(request.function, 'commit'):
            wd.add(paths=list(files))
            wd.commit(message='*')
    return wd


def pytest_collect_directory(path, parent):
    for compiled_module in path.listdir("*.pyc"):
        if not compiled_module.new(ext=".py").check():
            compiled_module.remove()

