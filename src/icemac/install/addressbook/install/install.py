from __future__ import absolute_import

from .. import CURRENT_NAME
from ..cmd import call_cmd
from ..utils import symlink
from .config import Configurator
from .config import USER_INI
from icemac.install.addressbook._compat import Path
import archive
import argparse
import configparser
import os
import os.path
import pdb  # noqa
import requests
import shutil
import sys
import tempfile
import z3c.recipe.usercrontab


requests_session = requests.Session()
try:
    import requests_file
except ImportError:  # pragma: no cover
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
            dir_name = Path(file.namelist()[0].strip('/'))
            if dir_name.exists():
                raise RuntimeError('{!r} already exists.'.format(
                    str(dir_name)))
            file.extract()
            return dir_name
        finally:
            del file  # make sure __del__ of file is called


def remove_cronjobs(path, readcrontab=None, writecrontab=None):
    """Remove cron jobs generated by previous ab version from crontab file.

    The arguments `readcrontab` and `writecrontab` are only for testing
    purposes.
    """
    path = Path(path).resolve().absolute()
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


def not_matched_prerequisites(path):
    """Check whether icemac.addressbook can be installed."""
    if (path / 'buildout.cfg').exists():
        return (
            "ERROR: buildout.cfg already exists.\n"
            "       Please (re-)move the existing one and restart install.")
    if sys.version_info[:2] != (2, 7):
        return ("ERROR: icemac.addressbook currently supports only Python 2.7."
                "\n       But you try to install it using Python %s.%s.%s." % (
                    sys.version_info[:3]))
    return False


def install(dir_name, stdin=None):
    """Configure the address book extracted to `dir_name`."""
    msg = not_matched_prerequisites(dir_name)
    if msg:
        print(msg)
        sys.exit(-1)
    cwd = Path.cwd()
    conf_args = []
    curr_path = cwd / CURRENT_NAME
    if curr_path.exists():
        conf_args.append(curr_path / USER_INI)
        remove_cronjobs(CURRENT_NAME)

    os.chdir(str(dir_name))  # PY2: in PY3 `str` is no longer needed
    try:
        if Configurator(*conf_args, stdin=stdin)():
            call_cmd('running bin/buildout', '../bin/buildout')
            migrate()
    finally:
        os.chdir(str(cwd))  # PY2: in PY3 `str` is no longer needed
    print('Installation complete.')


def migration_bool_get(config, key, default=None):
    """Read value from "migration" section of the config."""
    try:
        value = config.get('migration', key)
    except (configparser.NoOptionError,
            configparser.NoSectionError):
        assert default is not None
        return default
    return value == 'yes'


def copy_dir(src_base, dest_base, *path_parts):
    """Copy directory from src_base + path_parts to dest_base + path_parts."""
    path = os.path.join(*path_parts)
    src_dir = os.path.join(src_base, path)
    dest_dir = os.path.join(dest_base, path)
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)
    shutil.copytree(src_dir, dest_dir)


def delete_dir_contents(*path_parts):
    """Remove the contents of a directory, but keep the directory.

    Currently it is deleted and recreated afterwards.
    """
    path = os.path.join(*path_parts)
    shutil.rmtree(path)
    os.mkdir(path)


def migrate():
    """Migrate an old address book instance."""
    # Read the ini file the configurator just created to get the
    # migration options.
    config = configparser.ConfigParser()
    config.read(USER_INI)

    if not migration_bool_get(config, 'do_migration', default=False):
        # no migration wanted
        return False
    old_instance = config.get('migration', 'old_instance', fallback='')
    if not (old_instance and
            os.path.exists(os.path.join(old_instance, USER_INI))):
        print('ERROR: You did not provide a path to the old instance.')
        print('       Or the path does not point to a previous instance.')
        print('       So I can not migrate the existing content.')
        sys.exit(-1)
    cwd = os.getcwd()
    try:
        os.chdir(old_instance)
        controller_path = os.path.join('bin', 'svctl')
        shutdown_command = 'shutdown'
        daemon_path = os.path.join('bin', 'svd')
        if not os.path.exists(controller_path):
            # Backwards compatibility up to version 7.x:
            controller_path = os.path.join('bin', 'addressbook')
            shutdown_command = 'stop'
        if migration_bool_get(config, 'stop_server'):
            call_cmd(
                'Stopping old instance', controller_path, shutdown_command)
        call_cmd('Creating backup of old instance',
                 os.path.join('bin', 'snapshotbackup'))
        print('Copying data backups to new instance ...')
        copy_dir(os.curdir, cwd, 'var', 'snapshotbackups')
        print('Copying blob backups to new instance ...')
        copy_dir(os.curdir, cwd, 'var', 'blobstoragesnapshots')
    finally:
        os.chdir(cwd)

    call_cmd('Restoring backup into new instance',
             os.path.join('bin', 'snapshotrestore'), '--no-prompt')

    # Backups are no longer needed after successful restore:
    delete_dir_contents(cwd, 'var', 'blobstoragesnapshots')
    delete_dir_contents(cwd, 'var', 'snapshotbackups')

    if migration_bool_get(config, 'start_server'):
        call_cmd('Starting new instance', daemon_path)
    return True


def main(args=None):
    """Entry point for `bin/install-addressbook`."""
    parser = argparse.ArgumentParser(
        description='Install a new version of the address book.')
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
