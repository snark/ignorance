import ignorance
import os
try:
    # pathlib is in python stdlib in python 3.5+
    from pathlib import Path
except ImportError:
    from pathlib2 import Path


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


def test_directory_only(tmpdir_builder):
    path = tmpdir_builder.setup('git/directory-only')
    pathobj = Path(path)
    files = []
    for r, d, fs in ignorance.git.walk(path):
        fs = [str(Path(os.path.join(r, f)).relative_to(pathobj)) for f in fs]
        files.extend(fs)
    assert 'foo/bar' not in files
    assert 'foo/baz' not in files
    assert 'foo/foo' not in files
    assert 'bar/bar' not in files
    assert 'bar/baz' not in files
    assert 'bar/foo' not in files
    assert 'baz/bar' not in files
    # foo/ is directory only, so...
    assert 'baz/foo' in files
    # Unmatched by anything.
    assert 'baz/baz' in files


def test_anchoring(tmpdir_builder):
    path = tmpdir_builder.setup('git/anchoring')
    pathobj = Path(path)
    files = []
    for r, d, fs in ignorance.git.walk(path):
        fs = [str(Path(os.path.join(r, f)).relative_to(pathobj)) for f in fs]
        files.extend(fs)
    # foo is unanchored
    assert not any([f for f in files if 'foo' in f])
    # dir_a/bar is anchored to the .gitignore file
    assert 'dir_a/bar' not in files
    assert 'dir_b/dir_a/bar' in files
    # dir_a/baz is not anchored, due to a double-asterisk
    assert 'dir_a/baz' not in files
    assert 'dir_b/dir_a/baz' not in files
    # */zap is anchored to the .gitignore file
    assert 'dir_a/zap' not in files
    assert 'dir_b/zap' not in files
    assert 'dir_c/zap' not in files
    assert 'dir_b/dir_a/zap' in files
    assert 'dir_c/1/zap' in files
    assert 'dir_c/2/1/zap' in files
    # Any quux under dir_c should be ignored, due to a double-asterisk
    assert 'dir_a/quux' in files
    assert 'quux' in files
    assert 'dir_c/quux' not in files
    assert 'dir_c/1/quux' not in files
    assert 'dir_c/2/1/quux' not in files
    # Leading slash anchors to the root
    assert 'xyzzy' not in files
    assert 'dir_a/xyzzy' in files
    # Finally, any .eggs file under spam/ should be ignored
    assert 'dir_a/spam.eggs' in files
    assert 'spam/ham/eggs' in files
    assert 'spam/spam/eggs' in files
    assert 'spam/ham.eggs' not in files
    assert 'spam/ham/ham.eggs' not in files
    assert 'spam/ham/spam.eggs' not in files
    assert 'spam/spam/ham.eggs' not in files
    assert 'spam/spam/spam.eggs' not in files
