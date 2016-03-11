import ignorance
import itertools
try:
    # pathlib is in python stdlib in python 3.5+
    from pathlib import Path
except ImportError:
    from pathlib2 import Path
import pytest
try:
    from unittest import mock
except ImportError:
    import mock


def test_rule_from_pattern_noops():
    to_test = [
        '', '#', '# Comment', '/', ' ', 'foo/***/bar', 'foo**bar'
    ]
    for pattern in to_test:
        rule = ignorance.git.rule_from_pattern(pattern)
        assert rule is None


def test_rule_from_pattern_basepath():
    foo = ignorance.git.rule_from_pattern('foo')
    assert foo.base_path is None
    foo = ignorance.git.rule_from_pattern('foo', base_path='/')
    assert foo.base_path == Path('/')
    foo = ignorance.git.rule_from_pattern('foo', base_path='/foo/bar/baz')
    assert foo.base_path == Path('/foo/bar/baz')
    with pytest.raises(ValueError) as einfo:
        ignorance.git.rule_from_pattern('foo', '.')
    assert str(einfo.value) == 'base_path must be absolute'


def test_rule_from_pattern_basics():
    foo_rule = ignorance.git.rule_from_pattern('foo', source=('some_path', 1))
    assert foo_rule.source == ('some_path', 1)

    to_test = [
        'foo', 'ba[rz]', 'ba?', '*.foo', 'foo/bar', 'foo/*/bar', '/foo',
        '/foo/bar', '**/foo/bar', 'foo/**/bar', 'foo/bar/**'
    ]
    for pattern in to_test:
        for negation, dir_only in itertools.product(
                (True, False), (True, False)):
            if negation:
                pattern = '!' + pattern
            if dir_only:
                pattern = pattern + '/'

            rule = ignorance.git.rule_from_pattern(pattern)
            assert rule.pattern == pattern
            if pattern[0] == '!':
                assert rule.negation is True
                pattern = pattern[1:]
            else:
                assert rule.negation is False
            if pattern[-1] == '/':
                assert rule.directory_only is True
                pattern = pattern[0:-1]
            else:
                assert rule.directory_only is False
            expected_rexp = ignorance.utils.fnmatch_pathname_to_regex(pattern)
            if '**' in pattern:
                pass
            elif '/' not in pattern:
                assert rule.regex == expected_rexp
                assert not rule.anchored
            else:
                if pattern[0] == '/':
                    expected_rexp = expected_rexp[1:]
                assert rule.regex == '^' + expected_rexp
                assert rule.anchored


def test_rule_from_pattern_double_asterisks():
    # Notably, our current fnmatch-based regexes don't handle trailing
    # values. This isn't a problem in the context of os.walk, but might
    # make things more difficult for a straight match.
    start = ignorance.git.rule_from_pattern('**/foo/bar')
    assert start.match('foo/bar')
    assert start.match('foo/bar/')
    assert start.match('zap/foo/bar')
    assert start.match('baz/zap/foo/bar')
    assert not start.match('foo/baz/bar')
    assert not start.match('foo/baz')
    assert not start.match('fop/bar')
    middle = ignorance.git.rule_from_pattern('foo/**/bar')
    assert middle.match('foo/bar')
    assert middle.match('foo/bar/')
    assert middle.match('foo/baz/bar')
    assert middle.match('foo/baz/zap/bar')
    assert not middle.match('bar/foo/bar')
    assert not middle.match('foo/baz')
    assert not middle.match('fop/bar')
    end = ignorance.git.rule_from_pattern('foo/**')
    assert end.match('foo/baz/bar')
    assert end.match('foo/baz')
    assert not end.match('foo')
    assert not end.match('foo/')


def test_rules_from_file(mocker):
    expected = ['foo', '#comment', 'bar']
    mf = mock.mock_open(read_data='\n'.join(expected))
    mf.return_value.__iter__ = lambda self: iter(expected)
    mf.return_value.__next__ = lambda self: self.readline()
    mocker.patch('ignorance.git.open', mf, create=True)
    rules = ignorance.git.rules_from_file('_', '/somepath')
    assert len(rules) == 2
    assert rules[0].pattern == 'foo'
    assert rules[0].source == ('/somepath/_', 1)
    assert rules[1].pattern == 'bar'
    assert rules[1].source == ('/somepath/_', 3)
    expected = []
    rules = ignorance.git.rules_from_file('_', '/somepath')
    assert len(rules) == 0
