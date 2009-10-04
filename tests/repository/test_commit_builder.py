import py
from anyvc.common.commit_builder import CommitBuilder


class FakeCommit(object):
    def __init__(self, file_tree):
        self.file_tree = file_tree

@py.test.mark.xfail
def test_rename():
    base_commit = FakeCommit({
        'test':{
            'test.py':'#!/usr/bin/python',
            },
        })

    commit_builder = CommitBuilder(None, base_commit, author='test')

    commit_builder.mkdir('test2')
    commit_builder.rename('test/test.py', 'test2/test.py')

    content = commit_builder.read('test2/test.py')
    assert content == '#!/usr/bin/python'
