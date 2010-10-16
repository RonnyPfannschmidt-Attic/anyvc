import py
from tests.helpers import  VcsMan
import os

from anyvc import metadata

pytest_plugins = "doctest"

test_in_interpreters = 'python2', 'python3', 'jython', 'pypy'

test_on = {
    '%s': None,
    'remote/%s': 'popen',
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
    if vcs is None:
        return
    vcs = vcs.split('-')[0]
    if vcs not in metadata.backends:
        if vcs in metadata.aliases:
            vcs = metadata.aliases[vcs]
            config.option.vcs = vcs
        else:
            raise KeyError(vcs, '%r not found' % vcs)


    os.environ['BZR_EMAIL'] = 'Test <test@example.com>'

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
    """
    create a cached backend instance that is used the whole session
    makes instanciating backend cheap
    """
    vc, spec = request.param
    return request.cached_setup(
            lambda: metadata.get_backend(vc, spec),
            extrakey=request.param,
            scope='session')


def pytest_funcarg__mgr(request):
    """
    create a preconfigured :class:`tests.helplers.VcsMan` instance
    pass the currently tested backend 
    and create a tmpdir for the vcs/test combination

    auto-check for the vcs features and skip if necessary
    """
    vc, spec = request.param
    r = spec or 'local'
    testdir = request.getfuncargvalue('tmpdir')
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
    """
    create a repo below mgf called 'repo'
    """
    return request.getfuncargvalue('mgr').make_repo('repo')

def pytest_funcarg__wd(request):
    """
    create a workdir below mgr called 'wd'
    if the feature "wd:heavy" is not supported use repo as help
    """
    mgr = request.getfuncargvalue('mgr')
    if 'wd:heavy' not in mgr.backend.features:
        repo = request.getfuncargvalue('repo')
        wd = mgr.create_wd('wd', repo)
    else:
        wd = mgr.create_wd('wd')

    fp = request.function
    if hasattr(fp, 'files'):
        files = fp.files.args[0]
        wd.put_files(files)
        assert wd.has_files(*files)
        if  hasattr(fp, 'commit'):
            wd.add(paths=list(files))
            wd.commit(message='initial commit')
    return wd


def pytest_collect_directory(path, parent):
    for compiled_module in path.listdir("*.pyc"):
        if not compiled_module.new(ext=".py").check():
            compiled_module.remove()

