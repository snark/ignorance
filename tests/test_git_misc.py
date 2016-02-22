from ignorance import git


def test_strict_subpath():
    assert git.strict_subpath('/foo/bar', '/foo/bar') == ''
    assert git.strict_subpath('/foo/bar/', '/foo/bar') == ''
    assert git.strict_subpath('/foo/bar', '/foo/bar/') == ''
    assert git.strict_subpath('/foo', '/foo/bar/') == 'bar'
    assert git.strict_subpath('/foo/', '/foo/bar/') == 'bar'
    assert git.strict_subpath('/foo', '/foo/bar') == 'bar'
    assert git.strict_subpath('/foo/', '/foo/bar') == 'bar'
    assert git.strict_subpath('/foo/', '/foo/bar/baz') == 'bar/baz'
    assert git.strict_subpath('/', '/foo/bar/baz') == 'foo/bar/baz'
