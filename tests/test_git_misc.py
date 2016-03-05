import ignorance


def test_rule_from_pattern_basics():
    to_test = [
        'foo', 'ba[rz]', 'ba?', '*.foo', 'foo/bar', 'foo/*/bar', '/foo',
        '/foo/bar', '**/foo/bar', 'foo/**/bar', 'foo/bar/**'
    ]
    negations = ['!' + pattern for pattern in to_test]
    for pattern in to_test + negations:
        rule = ignorance.git.rule_from_pattern(pattern)
        assert rule.pattern == pattern
        if pattern[0] == '!':
            assert rule.negation is True
            pattern = pattern[1:]
        else:
            assert rule.negation is False
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
