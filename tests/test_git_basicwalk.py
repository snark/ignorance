# content of test_git_basicwalk.py
from ignorance import git

def test_strict_subpath():
    assert git.strict_subpath('/foo/bar', '/foo/bar') == ''
    assert git.strict_subpath('/foo/bar/', '/foo/bar') == ''
    assert git.strict_subpath('/foo/bar', '/foo/bar/') == ''


