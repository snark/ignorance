# -*- coding: utf-8 -*-
import collections
import os
import re
try:
    # pathlib is in python stdlib in python 3.5+
    from pathlib import Path
except ImportError:
    from pathlib2 import Path

whitespace_re = re.compile(r'(\\ )+$')

IGNORE_RULE_FIELDS = [
    'pattern', 'regex',  # Basic values
    'negation', 'directory_only', 'anchored',  # Behavior flags
    'base_path',  # Meaningful for gitignore-style behavior
    'source'  # (file, line) tuple for reporting
]


class IgnoreRule(collections.namedtuple('IgnoreRule_', IGNORE_RULE_FIELDS)):
    # TODO Add source to __str__ or perhaps a method
    def __str__(self):
        return self.pattern

    def __repr__(self):
        return ''.join(['IgnoreRule(\'', self.pattern, '\')'])

    def match(self, abs_path):
        matched = False
        rel_path = str(Path(abs_path).relative_to(self.base_path))
        if rel_path.startswith('./'):
            rel_path = relpath[2:]
        if re.search(self.regex, rel_path):
            matched = True
        return matched


# Frustratingly, python's fnmatch doesn't provide the FNM_PATHNAME
# option that .gitignore's behavior depends on.
def fnmatch_pathname_to_regex(pattern):
    """
    Implements fnmatch style-behavior, as though with FNM_PATHNAME flagged;
    the path seperator will not match shell-style '*' and '.' wildcards.
    """
    i, n = 0, len(pattern)
    nonsep = ''.join(['[^', os.sep, ']'])
    res = []
    while i < n:
        c = pattern[i]
        i = i + 1
        if c == '*':
            try:
                if pattern[i] == '*':
                    i = i + 1
                    res.append('.*')
                    if pattern[i] == '/':
                        i = i + 1
                        res.append(''.join([os.sep, '?']))
                else:
                    res.append(''.join([nonsep, '*']))
            except IndexError:
                res.append(''.join([nonsep, '*']))
        elif c == '?':
            res.append(nonsep)
        elif c == '/':
            res.append(os.sep)
        elif c == '[':
            j = i
            if j < n and pattern[j] == '!':
                j = j + 1
            if j < n and pattern[j] == ']':
                j = j + 1
            while j < n and pattern[j] != ']':
                j = j+1
            if j >= n:
                res.append('\\[')
            else:
                stuff = pattern[i:j].replace('\\', '\\\\')
                i = j+1
                if stuff[0] == '!':
                    stuff = ''.join('^', stuff[1:])
                elif stuff[0] == '^':
                    stuff = ''.join('\\' + stuff)
                res.append('[{}]'.format(stuff))
        else:
            res.append(re.escape(c))
    res.append('\Z(?ms)')
    return ''.join(res)
