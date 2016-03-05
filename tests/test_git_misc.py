import ignorance
import itertools


def test_rule_from_pattern_basics():
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
