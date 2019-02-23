from __future__ import absolute_import

from .. import DIRNAME_TEMPLATE
from ..utils import symlink
import argparse


def main(args=None):
    """Entry point for `bin/make-current-addressbook`."""
    parser = argparse.ArgumentParser(
        description='Update the `current` symlink to a given address book '
                    'version.')
    parser.add_argument(
        'version',
        help='Version number of the icemac.addressbook package you want to '
             'make the current one.')

    args = parser.parse_args(args)
    symlink(DIRNAME_TEMPLATE.format(args.version))
