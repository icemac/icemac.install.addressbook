from __future__ import absolute_import

from . import CURRENT_NAME, DIRNAME_TEMPLATE
from .cmd import call_cmd
import archive
import argparse
import os
import os.path
import pdb  # noqa
import requests
import shutil
import sys
import tempfile


requests_session = requests.Session()
try:
    import requests_file
except ImportError:  # pragma: nocover
    # We are not running the tests now:
    pass
else:
    requests_session.mount('file://', requests_file.FileAdapter())


PYPI_JSON_URL = (
    'https://pypi.python.org/pypi/icemac.addressbook/json')


def download_url(version):
    """Get the download_url."""
    r = requests_session.get(PYPI_JSON_URL)
    r.raise_for_status()
    data = r.json()
    releases = data['releases']
    if version is None:
        version = data['info']['version']
    try:
        packages = releases[version]
    except KeyError:
        raise ValueError('Release {!r} does not exist.'.format(version))
    for package in packages:
        if package['packagetype'] == 'sdist':
            return package['url']
    raise ValueError(
        'Release {!r} does not have an sdist release.'.format(version))


def extract_archive_from(url):
    """Download and archive from `url` and extract it to the current directory.

    Returns the path to the extracted directory.
    """
    r = requests_session.get(url, stream=True)
    r.raise_for_status()
    r.raw.decode_content = True
    with tempfile.NamedTemporaryFile() as download_file:
        shutil.copyfileobj(r.raw, download_file)
        download_file.seek(0)
        try:
            file = archive.Archive(download_file, r.url or url)
            dir_name = file.namelist()[0].strip('/')
            if os.path.exists(dir_name):
                raise RuntimeError('{!r} already exists.'.format(dir_name))
            file.extract()
            return dir_name
        finally:
            del file  # make sure __del__ of file is called


def install(dir_name, stdin=None):
    """Run the address book installer in `dir_name`."""
    cwd = os.getcwd()
    args = [sys.executable, 'install.py']
    if os.path.exists(CURRENT_NAME):
        args.append(os.path.join(os.pardir, CURRENT_NAME))
    os.chdir(dir_name)
    try:
        call_cmd(*args)
    finally:
        os.chdir(cwd)


def symlink(dir_name):
    """Create or update the `current` symlink to point to `dir_name`."""
    if os.path.lexists(CURRENT_NAME):
        os.unlink(CURRENT_NAME)
    os.symlink(dir_name, CURRENT_NAME)


def make_current(args=None):
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


def main(args=None):
    """Entry point for `bin/update-addressbook`."""
    parser = argparse.ArgumentParser(
        description='Update the address book to a new version.')
    parser.add_argument(
        'version',
        nargs=argparse.OPTIONAL,
        help='Version number of the icemac.addressbook package you want to '
             'install. Defaults to the newest version.')
    parser.add_argument(
        '--debug', action="store_true",
        help='Enter debugger on errors.')

    args = parser.parse_args(args)
    try:
        url = download_url(args.version)
        try:
            dir_name = extract_archive_from(url)
        except RuntimeError as e:
            print e
            return
        install(dir_name)
        symlink(dir_name)
    except Exception:
        if args.debug:
            pdb.post_mortem()
        else:
            raise
