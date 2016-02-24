import ignorance
import os


def test_basic_walk():
    test_path = os.path.realpath(__file__)
    data_path = os.path.realpath(os.path.join(test_path, '../data/git'))
    files = []
    for r, d, f in ignorance.git.walk(os.path.join(data_path, 'basic')):
        files.extend(f)
    assert files == ['.gitignore', 'bam', 'foo', 'ignored', 'zap']

def test_overrides():
    test_path = os.path.realpath(__file__)
    data_path = os.path.realpath(os.path.join(test_path, '../data/git'))
    files = []
    for r, d, f in ignorance.git.walk(os.path.join(data_path, 'override')):
        files.extend(f)
    assert 'bar' in files
    assert 'baz.tmpx' in files
    assert 'override.tmp' in files
    assert 'quux' in files
    assert 'foo.tmp' not in files
    assert 'order_counts.tmp' not in files
