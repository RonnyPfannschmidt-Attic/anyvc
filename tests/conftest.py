import py
import pytest
from tests.helpers import VcsMan
import os

from anyvc import metadata

pytest_plugins = "doctest"
test_in_interpreters = 'python2', 'python3', 'jython', 'pypy'


def pytest_addoption(parser):
    g = parser.getgroup('anyvc')
    g.addoption("--local-remoting", action="store_true", default=False,
                help='test via execnet remoting')
    g.addoption("--no-direct-api", action="store_true", default=False,
                help='don\'t test the direct api')
    g.addoption("--vcs", action='store', default=None)


def pytest_configure(config):
    vcs = config.getvalue('vcs')
    if vcs is None:
        return
    vcs = vcs.split('-')[0].strip('0123456789')
    if vcs not in metadata.backends:
        if vcs in metadata.aliases:
            vcs = metadata.aliases[vcs]
            config.option.vcs = vcs
        else:
            raise KeyError(vcs, '%r not found' % vcs)

    os.environ['BZR_EMAIL'] = 'Test <test@example.com>'


@pytest.fixture(scope='session', params=['direct', 'popen'])
def spec(request):
    direct = request.param == 'direct'
    if request.config.getvalue('no_direct_api') and direct:
        pytest.skip('no direct api testing')
    if not request.config.getvalue('local_remoting') and not direct:
        pytest.skip('no remote testing')
    from execnet.xspec import XSpec
    return XSpec(request.param)


@pytest.fixture(scope='session', params=metadata.backends)
def vcs(request):
    wanted = request.config.getvalue('vcs')
    if wanted and request.param != wanted:
        pytest.skip('%s not wanted for this test run' % request.param)
    return request.param


@pytest.fixture(scope='session')
def backend(vcs, spec):
    """
    create a cached backend instance that is used the whole session
    makes instanciating backend cheap
    """
    if spec.direct:
        spec = None
        return metadata.get_backend(vcs, spec)


@pytest.fixture()
def mgr(spec, backend, tmpdir, request):
    """
    create a preconfigured :class:`tests.helplers.VcsMan` instance
    pass the currently tested backend
    and create a tmpdir for the vcs/test combination

    auto-check for the vcs features and skip if necessary
    """
    required_features = getattr(request.function, 'feature', None)

    if required_features:
        required_features = set(required_features.args)
        difference = required_features.difference(backend.features)
        print required_features
        if difference:
            py.test.skip('%s lacks features %r' % (
                backend,
                sorted(difference)))

    return VcsMan(backend.name, tmpdir, spec, backend)


@pytest.fixture()
def repo(mgr):
    """
    create a repo below mgf called 'repo'
    """
    return mgr.make_repo('repo')


@pytest.fixture()
def wd(mgr, repo, request):
    #XXX: repo only needed when light backends
    """
    create a workdir below mgr called 'wd'
    if the feature "wd:heavy" is not supported use repo as help
    """
    if 'wd:heavy' not in mgr.backend.features:
        wd = mgr.create_wd('wd', repo)
    else:
        wd = mgr.create_wd('wd')
    return wd


@pytest.fixture(autouse=True)
def prepared_files(request):
    fp = request.function
    if hasattr(fp, 'files'):
        wd = request.getfuncargvalue('wd')
        files = fp.files.args[0]
        wd.put_files(files)
        assert wd.has_files(*files)
        if  hasattr(fp, 'commit'):
            wd.add(paths=list(files))
            wd.commit(message='initial commit')
