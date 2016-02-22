import ignorance
import os

def test_basic_walk():
    test_path = os.path.realpath(__file__)
    data_path = os.path.realpath(os.path.join(test_path, '../data/git'))
    files = []
    for r, d, f in ignorance.git.walk(os.path.join(data_path, 'basic')):
        files.extend(f)
    assert files == ['.gitignore', 'bam', 'foo', 'ignored', 'zap']


