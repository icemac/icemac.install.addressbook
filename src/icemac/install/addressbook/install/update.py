from .. import CURRENT_NAME
from ..cmd import call_cmd
from .config import Configurator
from .config import USER_INI
from icemac.install.addressbook._compat import Path
import argparse
import os
import pdb  # noqa: T002
import sys


def update(stdin=None):
    """Update the current address book installation."""
    curr_path = Path.cwd() / CURRENT_NAME
    if not curr_path.exists():
        print("ERROR: There is no symlink named {!r} in the current"
              " directory.".format(CURRENT_NAME))
        print("This script cannot be called here.")
        sys.exit(-1)

    if (curr_path / 'buildout.cfg').exists():
        print("ERROR: '{}/buildout.cfg' already exists please (re-) move"
              " it.".format(CURRENT_NAME))
        sys.exit(-2)

    cwd = os.getcwd()
    os.chdir(str(curr_path))  # PY2: in PY3 `str` is no longer needed
    configurator = Configurator(
        curr_path / USER_INI, install_new_version=False, stdin=stdin)
    try:
        configurator()
        call_cmd('running bin/buildout', '../bin/buildout')
        if configurator.restart_server == 'yes':
            call_cmd('Restarting instance', 'bin/svctl', 'restart', 'all')
    finally:
        os.chdir(str(cwd))  # PY2: in PY3 `str` is no longer needed
    print('Done.')


def main(args=None):
    """Entry point for `bin/change-addressbook-config`."""
    parser = argparse.ArgumentParser(
        description='Update the current address book installation.')
    parser.add_argument(
        '--debug', action="store_true",
        help='Enter debugger on errors.')

    args = parser.parse_args(args)
    try:
        update()
    except Exception:
        if args.debug:
            pdb.post_mortem()
        else:
            raise
