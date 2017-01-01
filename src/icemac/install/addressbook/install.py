from .cmd import call_cmd
import argparse
import json
import os
import os.path
import requests
import sys
import urllib
import zipfile


requests_session = requests.Session()
try:
    import requests_file
except ImportError:  # pragma: nocover
    # We are not running the tests now:
    pass
else:
    requests_session.mount('file://', requests_file.FileAdapter())


PYPI_JSON_URL = (
    'https://pypi.python.org/simple/icemac.addressbook/json')
CURRENT_NAME = 'current'


def download_url(version):
    """Get the download_url."""
    with urllib.urlopen(PYPI_JSON_URL.format(version)) as f:
        data = json.load(f)
    releases = data['releases']
    try:
        packages = releases[version]
    except KeyError:
        raise ValueError('Release {!r} does not exist.'.format(version))
    for package in packages:
        if package['packagetype'] == 'sdist':
            return package['url']
    raise ValueError(
        'Release {!r} does not have an sdist release.'.format(version))


def extract_zipfile_from(url):
    """Download the zipfile from `url` and extract it to a temporary directory.

    Returns the path to the extraction directory.
    """
    r = requests_session.get(url, stream=True)
    with zipfile.ZipFile(r.raw) as zip_file:
        zip_file.extractall()
        return zip_file.namelist()[0].strip('/')


def install(dir_name, stdin=None):
    """Run the address book installer in `dir_name`."""
    cwd = os.getcwd()
    os.chdir(dir_name)
    args = [sys.executable, 'install.py']
    if os.path.exists(CURRENT_NAME):
        args.append(CURRENT_NAME)
    try:
        call_cmd(*args)
    finally:
        os.chdir(cwd)


def symlink(dir_name):
    """Create or update the `current` symlink to point to `dir_name`."""
    if os.path.lexists(CURRENT_NAME):
        os.unlink(CURRENT_NAME)
    os.symlink(dir_name, CURRENT_NAME)


def main(args=None):
    """Entry point for `bin/update-addressbook`."""
    parser = argparse.ArgumentParser(
        description='Update the address book to a new version.')
    parser.add_argument(
        'version',
        help='Version number of the icemac.addressbook package you want to '
             'install')

    args = parser.parse_args(args)
    url = download_url(args.version)
    dir_name = extract_zipfile_from(url)
    install(dir_name)
    symlink(dir_name)
