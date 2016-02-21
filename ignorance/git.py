# -*- coding: utf-8 -*-
import functools
import itertools
import os
import re
from . import utils
try:
    # scandir-powered walk is in the stdlib in python 3.5+
    from os import scandir  # NOQA
    from os import walk as _walk
except ImportError:
    # otherwise, grab it from scandir for the performance boost
    from scandir import walk as _walk


def strict_subpath(base_path, child_path):
    if os.path.join(child_path, '') == os.path.join(base_path, ''):
        return ''
    else:
        child_split = child_path.split(os.path.sep)
        base_split = base_path.split(os.path.sep)
        return os.path.join(
            *child_split[len(base_split):]
        )


def walk(directory, onerror=None, filename='.gitignore',
         ignore_completely=None):
    """
    Generate the file names in a directory tree by walking the tree
    top-down, while obeying the rules of .gitignore. Links will not
    be followed.
    """
    if ignore_completely is None:
        ignore_completely = ['.git']

    starting_directory = os.path.abspath(directory)

    # Rule list will be a dict of directory to (rule list, parent
    # directory) tuples
    rule_list = {}
    while True:
        for root, dirs, files in _walk(directory, onerror=onerror):
            rules = []
            if filename in files:
                with open(os.path.join(root, filename)) as ignore_file:
                    for line in ignore_file:
                        line = line.rstrip('\n')
                        rule = rule_from_pattern(line, os.path.abspath(root))
                        if rule:
                            rules.append(rule)
            current_dir = os.path.abspath(root)
            # SBC fix this up
            # We know we are either within the base_dir...
            rel_path = strict_subpath(starting_directory, current_dir)
            if rel_path == '':
                rule_list[''] = (rules, None)
            # ...or a child dir
            else:
                rule_list[rel_path] = (rules, os.path.dirname(rel_path))
            # Now, make a list of rules, working our way back to the
            # base directory.
            applicable_rules = []
            cursor = rule_list[rel_path]
            while cursor:
                applicable_rules.append(cursor[0])
                # Tiny hack for py2/py3 polyglot without using six
                if isinstance(cursor[1], (''.__class__, u''.__class__)):
                    cursor = rule_list[cursor[1]]
                else:
                    cursor = False
            # Our rules are actually ordered from the base down
            applicable_rules = applicable_rules[::-1]
            flat_list = list(
                itertools.chain.from_iterable(applicable_rules)
            )
            ignore = []
            for final_override in ignore_completely:
                ignore.append(final_override)
            for d in dirs:
                included = True
                path = os.path.abspath(os.path.join(root, d))
                for rule in flat_list:
                    if included != rule.negation:
                        if rule.match(path):
                            included = not included
                if not included:
                    ignore.append(d)
            dirs[:] = [d for d in dirs if d not in ignore]
            ignore = []
            for f in files:
                included = True
                path = os.path.join(root, f)
                for rule in flat_list:
                    if rule.directory_only:
                        continue
                    if included != rule.negation:
                        if rule.match(os.path.abspath(path)):
                            included = not included
                if not included:
                    ignore.append(f)
            files[:] = [f for f in files if f not in ignore]
            yield root, dirs, files
        return


def rule_from_pattern(pattern, base_path=None, source=None):
    """
    Take a .gitignore match pattern, such as "*.py[cod]" or "**/*.bak",
    and return an IgnoreRule suitable for matching against files and
    directories. Patterns which do not match files, such as comments
    and blank lines, will return None.

    Because git allows for nested .gitignore files, a base_path value
    is required for correct behavior. The base path should be absolute.
    """
    if base_path and base_path != os.path.abspath(base_path):
        raise ValueError('base_path must be absolute')
    # Early returns follow
    # Discard comments and seperators
    if pattern.strip() == '' or pattern[0] == '#':
        return
    # Discard anything with more than two consecutive asterisks
    if pattern.find('***') > -1:
        return
    # Discard anything with invalid double-asterisks -- they can appear
    # at the start or the end, or be surrounded by slashes
    for m in re.finditer(r'\*\*', pattern):
        start_index = m.start()
        if (start_index != 0 and start_index != len(pattern) - 2 and
                (pattern[start_index - 1] != '/' or
                 pattern[start_index + 2] != '/')):
            return

    # Store the exact pattern for our repr and string functions
    orig_pattern = pattern

    if pattern[0] == '!':
        negation = True
        pattern = pattern[1:]
    else:
        negation = False

    # Special-casing '/', which doesn't match any files or directories
    if pattern.strip() == '/':
        return

    directory_only = pattern[-1] == '/'
    # A slash is a sign that we're tied to the base_path of our rule
    # set.
    anchored = '/' in pattern[:-1]
    relative_path = functools.partial(strict_subpath, base_path or '')
    if pattern[0] == '/':
        pattern = pattern[1:]
    if pattern[0] == '*' and pattern[1] == '*':
        pattern = pattern[2:]
        anchored = False
    if pattern[0] == '/':
        pattern = pattern[1:]
    if pattern[-1] == '/':
        pattern = pattern[:-1]
    regex = utils.fnmatch_pathname_to_regex(
        pattern
    )
    if anchored:
        regex = ''.join(['^', regex])
    return utils.IgnoreRule(
        pattern=orig_pattern,
        regex=regex,
        negation=negation,
        directory_only=directory_only,
        anchored=anchored,
        relative_path=relative_path,
        source=source
    )
