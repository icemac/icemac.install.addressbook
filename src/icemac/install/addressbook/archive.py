from . import CURRENT_NAME
import argparse
import itertools
import os.path
import shutil

ARCHIVE_DIR_NAME = 'archive'
# Formats sorted by priority
DESIRED_ARCHIVE_FORMATS = ('xztar', 'bztar', 'gztar', 'zip', 'tar')


def archive(version):
    """Archive a directory named `icemac.addressbook-<version>`."""
    dirname = 'icemac.addressbook-{}'.format(version)
    if not os.path.exists(dirname):
        raise ValueError('Directory {!r} does not exist.'.format(dirname))
    if os.path.realpath(CURRENT_NAME).endswith(dirname):
        raise AssertionError(
            '{!r} is the current address book -- cannot archive it!'.format(
                dirname))
    if not os.path.exists(ARCHIVE_DIR_NAME):
        os.mkdir(ARCHIVE_DIR_NAME)
    supported_archive_formats = [x[0] for x in shutil.get_archive_formats()]
    format = next(itertools.ifilter(lambda x: x in supported_archive_formats,
                                    DESIRED_ARCHIVE_FORMATS))
    archive = shutil.make_archive(dirname, format, base_dir=dirname)
    shutil.move(archive, ARCHIVE_DIR_NAME)
    shutil.rmtree(dirname)
    return "{dirname} archived to {dir}/{target}".format(
        dirname=dirname, dir=ARCHIVE_DIR_NAME, target=archive)


def main(args=None):
    """Entry point for `bin/archive-addressbook`."""
    parser = argparse.ArgumentParser(
        description='Archive an old address book instance')
    parser.add_argument(
        'version',
        help='Version number of the old version used in the directory name')

    args = parser.parse_args(args)

    print archive(args.version)
