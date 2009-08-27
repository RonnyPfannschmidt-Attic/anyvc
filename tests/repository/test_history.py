import py


def test_build_first_commit(mgr):
    repo = mgr.make_repo('repo')
    with repo.transaction(message='initial', author='test') as root:
        with root.join('test.txt').open('w') as f:
            f.write("text")

    with repo.get_default_head() as root:
        with root.join("test.txt").open() as f:
            content = f.read()
            assert content == 'text'


def test_generate_commit_chain(mgr):
    from datetime import datetime
    repo = mgr.make_repo('repo')
    for i in range(1,11):
        with repo.transaction(
                message='test%s'%i,
                author='test') as root:
            with root.join('test.txt').open('w') as f:
                f.write("test%s"%i)

    assert len(repo) == 10

    head = repo.get_default_head()

    revs = [head]
    rev = head

    while rev.parents:
        rev = rev.parents[0]
        revs.append(rev)

    assert len(revs) == 10

    for i, rev in enumerate(reversed(revs)):
        with rev as root:
            with root.join('test.txt').open() as f:
                data = f.read()
                assert data == 'test%s'%(i+1)


def test_create_commit_at_time(mgr):
    if mgr.vc == 'subversion':
        py.test.skip('currently no support for setting the commit time on svn')

    from datetime import datetime
    repo = mgr.make_repo('repo')

    time = datetime(2000, 1, 1, 10, 0, 0)

    with repo.transaction(
            message='test',
            author='test',#XXX: author should be optional
            time=datetime(2000, 1, 1, 10, 0, 0)) as root:
        with root.join('test.txt').open('w') as f:
                f.write('test')

    head = repo.get_default_head()

    print repr(head.id)
    print head.time
    assert head.time == time


def test_create_commit_with_author(mgr):
    if mgr.vc == 'subversion':
        py.test.skip('currently no support for setting the commit author on svn')

    repo = mgr.make_repo('repo')

    with repo.transaction(
            message='test',
            author='test author ', #with whitespace
            ) as root:
        with root.join('test.txt').open('w') as f:
                f.write('test')

    head = repo.get_default_head()
    print repr(head.author)
    assert head.author == 'test author' #whitespace gone

