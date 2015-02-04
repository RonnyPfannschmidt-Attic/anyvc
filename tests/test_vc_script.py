import pytest
from click.testing import CliRunner
from anyvc.client import cli


@pytest.mark.files({'setup.py': 'pass'})
@pytest.mark.commited
def test_diff(wd):

    runner = CliRunner()
    res = runner.invoke(cli, [
        '-d', str(wd),
        'diff',
    ])

    assert res
