import ignorance


def test_basic_walk(tmpdir_builder):
    path = tmpdir_builder.setup('git/basic_match')
    files = []
    for r, d, f in ignorance.git.walk(path):
        files.extend(f)
    assert files == ['.gitignore', 'bam', 'foo', 'ignored', 'zap']


def test_negation(tmpdir_builder):
    path = tmpdir_builder.setup('git/negation')
    files = []
    for r, d, f in ignorance.git.walk(path):
        files.extend(f)
    assert 'bar' in files
    assert 'baz.tmpx' in files
    assert 'override.tmp' in files
    assert 'quux' in files
    assert 'foo.tmp' not in files
    assert 'order_counts.tmp' not in files
