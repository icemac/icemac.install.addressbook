from .cmd import call_cmd
import argparse
import os.path
import shutil

ARCHIVE_DIR_NAME = 'archive'


def archive(version):
    """Archive a directory named `icemac.addressbook-<version>`."""
    dirname = 'icemac.addressbook-{}'.format(version)
    if not os.path.exists(dirname):
        raise ValueError('Directory {!r} does not exist.'.format(dirname))
    if not os.path.exists(ARCHIVE_DIR_NAME):
        os.mkdir(ARCHIVE_DIR_NAME)
    target_archive = "{archive_dir}/{dirname}.tar.bz2".format(
        archive_dir=ARCHIVE_DIR_NAME, dirname=dirname)
    call_cmd('tar', '-cjf', target_archive, dirname)
    shutil.rmtree(dirname)
    return "{dirname} archived to {target}".format(
        dirname=dirname, target=target_archive)


def main(args=None):
    """Entry point for `bin/archive-addressbook`."""
    parser = argparse.ArgumentParser(
        description='Archive an old address book instance')
    parser.add_argument(
        'version',
        help='Version number of the old version used in the directory name')

    args = parser.parse_args(args)

    print archive(args.version)
