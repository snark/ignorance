import errno
import os
import pytest


class TmpDirBuilder:
    def __init__(self, tmpdir):
        self.tmpdir = tmpdir

    def setup(self, data_file_name):
        """
        Given a string representing a manifest file in our data directory (such
        as git/foo), instantiate all files listed under its files key. Files
        will be empty, unless followed by an indented block, which will
        represent the (text) contents of the file. A terminal slash in a
        manifest line creates a directory without creating a file.

        These manifests can be easily built with `tree -afFi --noreport`.
        """
        tmp_root = str(self.tmpdir)
        test_path = os.path.realpath(__file__)
        data_path = os.path.realpath(
            os.path.join(test_path, '../data/{}'.format(data_file_name))
        )
        with open(data_path, 'r') as f:
            lines = f.readlines()
            context = None
            # Strip empty lines
            lines = [l.rstrip('\n') for l in lines if l]
            for index, line in enumerate(lines):
                if line in ['.', './']:
                    continue
                if line.startswith('./'):
                    line = line[2:]
                if not line.startswith(' '):
                    line = os.path.join(tmp_root, line)
                    # We now have an absolute path to the file we wish to exist
                    context = {'filename': line, 'contents': []}
                else:
                    context['contents'].append(line.lstrip())
                if index + 1 == len(lines) or not lines[index + 1].\
                        startswith(' '):
                    # Write our file
                    path, fn = os.path.split(context['filename'])
                    try:
                        os.makedirs(path)
                    except OSError as e:
                        if e.errno == errno.EEXIST and os.path.isdir(path):
                            pass
                    if fn:
                        with open(context['filename'], 'w') as f:
                            f.write('\n'.join(context['contents']))
        return tmp_root


@pytest.fixture()
def tmpdir_builder(tmpdir):
    return TmpDirBuilder(tmpdir)
