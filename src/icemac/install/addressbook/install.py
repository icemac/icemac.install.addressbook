import os.path
from .cmd import call_cmd
import json
import os
import sys
import urllib
import zipfile


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


def extract_zipfile(file):
    """Extract a file object as a zip file to a temporary directory.

    Returns the path to the extraction directory.
    """
    with zipfile.ZipFile(file) as zip_file:
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
