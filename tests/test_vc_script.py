import pytest
from click.testing import CliRunner
from anyvc.client import cli


@pytest.fixture
def invoke(wd):
    def invoke(*args):
        start = '-d', str(wd)
        return invoke.runner.invoke(cli, start + args)

    invoke.runner = CliRunner()
    return invoke


@pytest.mark.files({'setup.py': 'pass'})
@pytest.mark.commited
def test_diff(invoke):
    res = invoke('diff')

    assert res
