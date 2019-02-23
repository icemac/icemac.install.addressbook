from __future__ import absolute_import

from .. import CURRENT_NAME
from ..utils import symlink
from ..cmd import call_cmd
import archive
import argparse
import os
import os.path
import pathlib
import pdb  # noqa
import requests
import shutil
import sys
import tempfile
import z3c.recipe.usercrontab


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


def download_url_and_version(version):
    """Get the download_url and the version.

    If `version` is `None` use the newest version.
    """
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
            return package['url'], version
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


def remove_cronjobs(path, readcrontab=None, writecrontab=None):
    """Remove cron jobs generated by previous ab version from crontab file.

    The arguments `readcrontab` and `writecrontab` are only for testing
    purposes.
    """
    path = pathlib.Path(path).resolve().absolute()
    for section in ['cronstart', 'cronpack', 'cronbackup']:
        identifier = '{} [{}]'.format(path, section)
        manager = z3c.recipe.usercrontab.UserCrontabManager(
            identifier=identifier,
            writecrontab=writecrontab,
            readcrontab=readcrontab)
        manager.read_crontab()
        try:
            if manager.del_entry(identifier) != 1:
                print('Cannot remove section {0!r} from crontab:'
                      ' entry not found.'.format(identifier))
                print(
                    'Please check the cron file yourself using `crontab -e`.')
        finally:
            manager.write_crontab()


def install(dir_name, stdin=None):
    """Run the address book installer in `dir_name`."""
    cwd = os.getcwd()
    args = [sys.executable, 'install.py']
    if os.path.exists(CURRENT_NAME):
        args.append(os.path.join(os.pardir, CURRENT_NAME))
        remove_cronjobs(CURRENT_NAME)
    os.chdir(dir_name)
    try:
        call_cmd(*args)
    finally:
        os.chdir(cwd)


def main(args=None):
    """Entry point for `bin/install-addressbook`."""
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
        url, version = download_url_and_version(args.version)
        try:
            print('Downloading version {} of icemac.addressbook ...'.format(
                version))
            dir_name = extract_archive_from(url)
        except RuntimeError as e:
            print(e)
            return
        install(dir_name)
        symlink(dir_name)
    except Exception:
        if args.debug:
            pdb.post_mortem()
        else:
            raise
