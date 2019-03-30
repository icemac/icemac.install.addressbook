from __future__ import absolute_import

from .. import CURRENT_NAME
from ..utils import symlink
from .config import USER_INI
from .install import download_url_and_version, extract_archive_from, install
from .install import main
from .install import migrate
from .install import not_matched_prerequisites
from .install import remove_cronjobs
from icemac.install.addressbook._compat import Path
from icemac.install.addressbook.testing import create_script
from icemac.install.addressbook.testing import user_ini
import icemac.install.addressbook.testing
import io
import mock
import os.path
import pkg_resources
import pytest
import textwrap


example_zip_url = Path(pkg_resources.resource_filename(
    'icemac.install.addressbook',
    'fixtures/icemac.addressbook-8.0.1.zip')).as_uri()


example_tgz_url = Path(pkg_resources.resource_filename(
    'icemac.install.addressbook',
    'fixtures/icemac.addressbook-2.8.tar.gz')).as_uri()


@pytest.fixture('function')
def local_pypi():
    """Patch the call to PyPI to a file URL."""
    url = Path(pkg_resources.resource_filename(
        'icemac.install.addressbook',
        'fixtures/icemac.addressbook.json')).as_uri()
    with mock.patch('icemac.install.addressbook.install.install.PYPI_JSON_URL',
                    new=url):
        yield


@pytest.fixture('function')
def crontab_file(tmpdir):
    """Create a crontab file with contents."""
    crontab_file = tmpdir.join('crontab_file')
    tmpdir.mkdir('icemac.addressbook-8.0')
    tmpdir.join('current').mksymlinkto('icemac.addressbook-8.0')
    path = str(tmpdir.join('icemac.addressbook-8.0'))
    crontab_file.write(textwrap.dedent("""\
        @monthly /var/ab/clean-up

        # Generated by {0} [cronstart]
        @reboot /var/ab/current/bin/svd
        # END {0} [cronstart]

        # Generated by {0} [cronpack]
        @weekly /var/ab/current/bin/zeopack localhost:13072 --days=1
        # END {0} [cronpack]
    """.format(path)))
    yield crontab_file


@pytest.fixture('function')
def old_instance_dir(basedir):
    """Create a fake instance dir of a previous address book installation."""
    old_inst_dir = basedir.join('v8.0.3').ensure_dir()
    user_ini(old_inst_dir, 'migration')
    old_bin_dir = old_inst_dir.join('bin').ensure_dir()
    create_script(old_bin_dir, 'snapshotbackup')
    snapshotbackups_dir = old_inst_dir.join(
        'var', 'snapshotbackups').ensure_dir()
    snapshotbackups_dir.join('snap.bak').write('1')
    blobstoragesnapshots_dir = old_inst_dir.join(
        'var', 'blobstoragesnapshots').ensure_dir()
    blobstoragesnapshots_dir.join('blob_snap.bak').write('2')
    yield old_inst_dir


def test_install__main__1(local_pypi):
    """It calls some functions with appropriate parameters."""
    path = 'icemac.install.addressbook.install.install'
    with mock.patch(path + '.extract_archive_from') as extract_archive_from,\
            mock.patch(path + '.install') as install,\
            mock.patch(path + '.symlink') as symlink:
        extract_archive_from.return_value = 'icemac.addressbook-2.6.2'
        main(['2.6.2'])
    extract_archive_from.assert_called_with(
        'https://pypi.python.org/packages/16/28/'
        '6524d23dcdf5f40579b0bd81bb3ccfb5375a4093990b8a1d3780288442c6/'
        'icemac.addressbook-2.6.2.tar.gz')
    install.assert_called_with('icemac.addressbook-2.6.2')
    symlink.assert_called_with('icemac.addressbook-2.6.2')


def test_install__main__2(local_pypi, capsys):
    """It defaults to the newest version."""
    path = 'icemac.install.addressbook.install.install'
    with mock.patch(path + '.extract_archive_from') as extract_archive_from,\
            mock.patch(path + '.install'),\
            mock.patch(path + '.symlink'):
        main([])
    extract_archive_from.assert_called_with(
        'https://pypi.python.org/packages/f9/e6/'
        '3b40e95936e32fa3d46cc5807785217c6444c086e669ccffffe0a2dff6ee/'
        'icemac.addressbook-2.8.tar.gz')
    out, err = capsys.readouterr()
    assert [
        u"Downloading version 2.8 of icemac.addressbook ...",
        u""] == out.split("\n")


def test_install__main__2_5(basedir, capsys):
    """It does not overwrite an existing installation."""
    path = 'icemac.install.addressbook.install.install'
    extract_archive_from(example_zip_url)
    with mock.patch(path + '.download_url_and_version') as dl_url_and_version,\
            mock.patch(path + '.install') as install:
        dl_url_and_version.return_value = example_zip_url, '8.0.1'
        main(['2.0.1'])
    assert not install.called
    out, err = capsys.readouterr()
    assert [
        u"Downloading version 8.0.1 of icemac.addressbook ...",
        u"'icemac.addressbook-8.0.1' already exists.",
        u""] == out.split("\n")


def test_install__main__3():
    """It drops into pdb on an exception if required."""
    path = 'icemac.install.addressbook.install.install'
    with mock.patch(path + '.download_url_and_version',
                    side_effect=RuntimeError),\
            mock.patch('pdb.post_mortem') as post_mortem:
        main(['--debug'])
    post_mortem.assert_called_with()


def test_install__main__4():
    """It it raises the exception if debugger is not required."""
    path = 'icemac.install.addressbook.install.install'
    with mock.patch(path + '.download_url_and_version',
                    side_effect=RuntimeError),\
            pytest.raises(RuntimeError):
        main([])


def test_install__download_url_and_version__1(local_pypi):
    """It returns the URL to download the specified address book version."""
    assert ((
        'https://pypi.python.org/packages/dd/01/'
        '36f28ce3db10431ec21245233e6562fc609d8301003b981b28fb3aedcf67/'
        'icemac.addressbook-1.10.5.zip', '1.10.5') ==
        download_url_and_version('1.10.5'))


def test_install__download_url_and_version__2(local_pypi):
    """It raises a ValueError if the specified version does not exist."""
    with pytest.raises(ValueError) as err:
        download_url_and_version('24.11')
    assert "Release '24.11' does not exist." == str(err.value)


def test_install__download_url_and_version__3(local_pypi):
    """It raises a ValueError if the specified version has not sdist."""
    with pytest.raises(ValueError) as err:
        download_url_and_version('1.1.1')
    assert "Release '1.1.1' does not have an sdist release." == str(err.value)


def test_install__download_url_and_version__4(local_pypi):
    """It returns the URL of the newest address book version if ...

    called with `None` as version.
    """
    assert ((
        'https://pypi.python.org/packages/f9/e6/'
        '3b40e95936e32fa3d46cc5807785217c6444c086e669ccffffe0a2dff6ee/'
        'icemac.addressbook-2.8.tar.gz', '2.8') ==
        download_url_and_version(None))


def test_install__extract_archive_from__1(basedir):
    """It downloads a zip file from a url and extracts it to cwd."""
    extract_dir = extract_archive_from(example_zip_url)
    assert 'icemac.addressbook-8.0.1' == str(extract_dir)
    assert {'icemac.addressbook-8.0.1/install.default.ini'} == set(
        [str(x) for x in extract_dir.iterdir()])


def test_install__extract_archive_from__2(basedir):
    """It downloads a tgz file from a url and extracts it to cwd."""
    extract_dir = extract_archive_from(example_tgz_url)
    assert 'icemac.addressbook-2.8' == str(extract_dir)
    assert {
        'icemac.addressbook-2.8/__init__.py',
        'icemac.addressbook-2.8/install.py'} == set(
        [str(x) for x in extract_dir.iterdir()])


def test_install__extract_archive_from__3(basedir):
    """It raises a RuntimeError if the extract dir already exists."""
    extract_archive_from(example_tgz_url)
    with pytest.raises(RuntimeError) as err:
        extract_archive_from(example_tgz_url)
    assert "'icemac.addressbook-2.8' already exists." == str(err.value)


def test_install__install__1(basedir):
    """It runs the address book installer in the given directory."""
    buildout = basedir.join('bin').ensure_dir().join('buildout')
    buildout.write('#!/bin/bash\necho "Fake buildout called."')
    buildout.chmod(0o755)

    address_book_dir = extract_archive_from(example_zip_url)
    stdin = io.StringIO()
    input = [u'eggs', u'admin', u'passwd']
    with icemac.install.addressbook.testing.user_input(input, stdin):
        install(address_book_dir, stdin=stdin)
    assert {
        'icemac.addressbook-8.0.1/install.default.ini',
        'icemac.addressbook-8.0.1/buildout.cfg',
        'icemac.addressbook-8.0.1/admin.zcml',
        'icemac.addressbook-8.0.1/install.user.ini',
    } == set([str(x) for x in address_book_dir.iterdir()])


def test_install__install__2(basedir):
    """It calls `install.py` with `current` if it exists in cwd."""
    dir_path = Path(str(basedir.mkdir('icemac.addressbook-5.5.7')))
    Configurator = 'icemac.install.addressbook.install.install.Configurator'
    with mock.patch(Configurator) as Configurator:
        Configurator().return_value = False
        install(dir_path)
        Configurator.assert_called_with(stdin=None)

        Configurator.reset_mock()
        Configurator().return_value = False
        current_path = Path(str(basedir.mkdir(CURRENT_NAME)))
        install(dir_path)
        Configurator.assert_called_with(current_path / USER_INI, stdin=None)


def test_install__install__3(basedir, monkeypatch):
    """It stops if Python version requirements are not met."""
    monkeypatch.setattr("sys.version_info", (3, 0, 0, 'final', 0))
    dir_name = basedir.mkdir('icemac.addressbook')
    with pytest.raises(SystemExit) as err:
        install(dir_name)
    assert '-1' == str(err.value)


def test_install__symlink__1(basedir):
    """It creates a symlink named `current` to the given directory."""
    basedir.mkdir('icemac.addressbook-2.1.2')
    symlink('icemac.addressbook-2.1.2')
    assert os.path.islink(CURRENT_NAME)
    assert os.path.exists(CURRENT_NAME)  # assert the link is not broken
    assert os.path.realpath(CURRENT_NAME).endswith('icemac.addressbook-2.1.2')


def test_install__symlink__2(basedir):
    """It replaces an existing symlink."""
    basedir.mkdir('icemac.addressbook-2.1.2')
    basedir.mkdir('icemac.addressbook-2.1.3')
    symlink('icemac.addressbook-2.1.2')
    symlink('icemac.addressbook-2.1.3')
    assert os.path.islink(CURRENT_NAME)
    assert os.path.exists(CURRENT_NAME)  # assert the link is not broken
    assert os.path.realpath(CURRENT_NAME).endswith('icemac.addressbook-2.1.3')


def test_install__remove_cronjobs__1(basedir, crontab_file):
    """It removes all entries belonging to the path."""
    crontab_path = str(crontab_file)
    assert 0 != remove_cronjobs('current',
                                readcrontab="cat %s" % crontab_path,
                                writecrontab="cat >%s" % crontab_path)
    assert '@monthly /var/ab/clean-up\n' == crontab_file.read()


def test_install__remove_cronjobs__2(basedir, crontab_file, capsys):
    """It prints an error message if a job cannot be removed."""
    crontab_path = str(crontab_file)
    assert 0 != remove_cronjobs(crontab_file.dirname,
                                readcrontab="cat %s" % crontab_path,
                                writecrontab="cat >%s" % crontab_path)
    assert '@reboot /var/ab/current/bin/svd' in crontab_file.read()
    out, err = capsys.readouterr()
    assert 3 == out.count('Cannot remove section')


def test_install__not_matched_prerequisites__1(basedir):
    """It returns an error text if `buildout.cfg` already exists in `cwd`."""
    buildout_cfg = basedir.join('buildout.cfg')
    buildout_cfg.write('[buildout]')
    assert ('ERROR: buildout.cfg already exists.\n'
            '       Please (re-)move the existing one and restart install.' ==
            not_matched_prerequisites(basedir))


def test_install__not_matched_prerequisites__2(basedir):
    """It returns `False`:

    * if no `buildout.cfg` exists in `cwd` and
    * if the right python version is used.

    We expect that the version of the python which runs the tests matches the
    requirement.
    """
    assert False is not_matched_prerequisites(basedir)


def test_install__not_matched_prerequisites__3(monkeypatch, basedir):
    """It returns an error text for a too old python version.

    `icemac.addressbook` currently only runs with some Python versions. If
    another version is used, an error message is returned.
    """
    monkeypatch.setattr("sys.version_info", (2, 5, 6, 'final', 0))
    assert ('ERROR: icemac.addressbook currently supports only Python 2.7.'
            '\n       But you try to install it using Python 2.5.6.' ==
            not_matched_prerequisites(basedir))


def test_install__not_matched_prerequisites__4(monkeypatch, basedir):
    """It returns an error text for a too new python version."""
    monkeypatch.setattr("sys.version_info", (3, 0, 0, 'final', 0))
    assert ('ERROR: icemac.addressbook currently supports only Python 2.7.'
            '\n       But you try to install it using Python 3.0.0.' ==
            not_matched_prerequisites(basedir))


def test_install__migrate__1(basedir):
    """It returns `False` if the config file is malformed."""
    basedir.join(USER_INI).write('')
    assert not migrate()


def test_install__migrate__2(basedir):
    """It raises SystemExit if old_instance is not set."""
    user_ini(basedir, 'migration', do_migration='yes')
    with pytest.raises(SystemExit) as err:
        migrate()
    assert '-1' == str(err.value)


def test_install__migrate__3(basedir):
    """It raises SystemExit if old_instance dir doesn't contain a USER_INI."""
    user_ini(basedir, 'migration', do_migration='yes', old_instance='v8.0')
    basedir.join('v8.0').ensure_dir()
    with pytest.raises(SystemExit) as err:
        migrate()
    assert '-1' == str(err.value)


def test_install__migrate__4(
        basedir,
        old_instance_dir,
        capfd
):
    """It migrates the data from old_instance."""
    user_ini(basedir, 'migration',
             do_migration='yes',
             old_instance=old_instance_dir.basename,
             stop_server='no',
             start_server='no')
    bin_dir = basedir.join('bin').ensure_dir()
    create_script(bin_dir, 'snapshotrestore')

    assert migrate()
    out, err = capfd.readouterr()
    assert [
        u'Creating backup of old instance ...',
        u'bin/snapshotbackup',
        u'Copying data backups to new instance ...',
        u'Copying blob backups to new instance ...',
        u'Restoring backup into new instance ...',
        u'bin/snapshotrestore --no-prompt'] == out.splitlines()
    assert '' == err


def test_install__migrate__5(
        basedir,
        old_instance_dir,
        capfd
):
    """It starts/stops the instance during migration if requested.

    Additionally it removes the target directory if it exists.
    """
    create_script(old_instance_dir.join('bin'), 'svctl')
    user_ini(basedir, 'migration',
             do_migration='yes',
             old_instance=old_instance_dir.basename,
             stop_server='yes',
             start_server='yes')
    bin_dir = basedir.join('bin').ensure_dir()
    create_script(bin_dir, 'snapshotrestore')
    create_script(bin_dir, 'svd')
    basedir.join('var', 'snapshotbackups').ensure_dir()

    assert migrate()
    out, err = capfd.readouterr()
    assert [
        u'Stopping old instance ...',
        u'bin/svctl shutdown',
        u'Creating backup of old instance ...',
        u'bin/snapshotbackup',
        u'Copying data backups to new instance ...',
        u'Copying blob backups to new instance ...',
        u'Restoring backup into new instance ...',
        u'bin/snapshotrestore --no-prompt',
        u'Starting new instance ...',
        u'bin/svd'] == out.splitlines()
    assert '' == err


def test_install__migrate__6(
        basedir,
        old_instance_dir,
        capfd
):
    """It allows to migrate from version <= 7.x."""
    create_script(old_instance_dir.join('bin'), 'addressbook')
    user_ini(basedir, 'migration',
             do_migration='yes',
             old_instance=old_instance_dir.basename,
             stop_server='yes',
             start_server='yes')
    bin_dir = basedir.join('bin').ensure_dir()
    create_script(bin_dir, 'snapshotrestore')
    create_script(bin_dir, 'svd')

    assert migrate()
    out, err = capfd.readouterr()
    assert [
        u'Stopping old instance ...',
        u'bin/addressbook stop',
        u'Creating backup of old instance ...',
        u'bin/snapshotbackup',
        u'Copying data backups to new instance ...',
        u'Copying blob backups to new instance ...',
        u'Restoring backup into new instance ...',
        u'bin/snapshotrestore --no-prompt',
        u'Starting new instance ...',
        u'bin/svd'] == out.splitlines()
    assert '' == err
