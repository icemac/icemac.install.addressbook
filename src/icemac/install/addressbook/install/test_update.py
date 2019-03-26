from __future__ import absolute_import

from .. import CURRENT_NAME
from .config import USER_INI
from .update import main
from .update import update
from io import BytesIO
import configparser
import icemac.install.addressbook.testing
import mock
import pytest


def test_update__main__1():
    """It calls `update()` ."""
    path = 'icemac.install.addressbook.install.update'
    with mock.patch(path + '.update') as update:
        main([])
        update.assert_called_with()


def test_update__main__2():
    """It drops into pdb on an exception if required."""
    path = 'icemac.install.addressbook.install.update'
    with mock.patch(path + '.update', side_effect=RuntimeError),\
            mock.patch('pdb.post_mortem') as post_mortem:
        main(['--debug'])
    post_mortem.assert_called_with()


def test_update__main__3():
    """It it raises the exception if debugger is not required."""
    path = 'icemac.install.addressbook.install.update'
    with mock.patch(path + '.update', side_effect=RuntimeError),\
            pytest.raises(RuntimeError):
        main([])


def test_update__update__1(
        basedir,
        capfd
):
    """It:

    * runs the configurator
    * changes config
    * runs buildout
    * restarts the instance
    """
    current_dir = basedir.mkdir(CURRENT_NAME)
    current_bin_dir = basedir.join(CURRENT_NAME, 'bin').ensure_dir()
    icemac.install.addressbook.testing.create_script(current_bin_dir, 'svctl')
    icemac.install.addressbook.testing.create_install_default_ini(current_dir)
    icemac.install.addressbook.testing.user_ini(
        current_dir, 'install', eggs_dir='my-eggs')
    bin_dir = basedir.join('bin').ensure_dir()
    icemac.install.addressbook.testing.create_script(bin_dir, 'buildout')

    stdin = BytesIO()
    with icemac.install.addressbook.testing.user_input(['all-eggs'], stdin):
        update(stdin)
    out, err = capfd.readouterr()
    assert [
        u'Welcome to changing your icemac.addressbook installation',
        u'',
        u'Hint: to use the default value (the one in [brackets]),'
        u' enter no value.',
        u'',
        u' Directory to store python eggs: [my-eggs] ',
        u' Log-in name for the administrator: [me] '] == out.splitlines()[:6]
    assert [
        u' Package 1: [] ',
        u'The address book instance has to be restarted.',
        u'When it runs as demon process it can be restarted automatically'
        u' otherwise you have to restart it manually.',
        u' Should the instance be automatically restarted?: [yes] ',
        u'creating buildout.cfg ...',
        u'saving config ...',
        u'running bin/buildout ...',
        u'../bin/buildout',
        u'Restarting instance ...',
        u'bin/svctl restart all',
        u'Done.'] == out.splitlines()[-11:]
    assert [
        '[buildout]\n',
        'extends = profiles/prod.cfg\n',
        'newest = true\n',
        'allow-picked-versions = true\n',
        'eggs-directory = all-eggs\n',
    ] == current_dir.join('buildout.cfg').readlines()[:5]
    cp = configparser.ConfigParser()
    cp.read(str(current_dir.join(USER_INI)))
    assert 'all-eggs' == cp.get('install', 'eggs_dir')
    # The value is not changed:
    assert 'no' == cp.get('migration', 'start_server')


def test_update__update__2(basedir):
    """It does not restart the instance if not chosen to."""
    current_dir = basedir.mkdir(CURRENT_NAME)
    icemac.install.addressbook.testing.create_install_default_ini(current_dir)
    icemac.install.addressbook.testing.user_ini(
        current_dir, 'install', eggs_dir='my-eggs')
    bin_dir = basedir.join('bin').ensure_dir()
    icemac.install.addressbook.testing.create_script(bin_dir, 'buildout')

    stdin = BytesIO()
    with icemac.install.addressbook.testing.user_input(
            # The question about restarting the instance is currently the
            # 13th one:
            [''] * 12 + ['no'], stdin):
        update(stdin)


def test_update__update__3(basedir, capsys):
    """It prints error text and exits if `current` doesn't exist in cwd."""
    with pytest.raises(SystemExit) as err:
        update()
    assert '-1' == str(err.value)
    out, err = capsys.readouterr()
    assert out.startswith("ERROR: There is no symlink named 'current'")


def test_update__update__4(basedir, capsys):
    """It prints error text and exits if `buildout.cfg` exists in cwd."""
    current_dir = basedir.mkdir(CURRENT_NAME)
    current_dir.join('buildout.cfg').write('[buildout]')
    with pytest.raises(SystemExit) as err:
        update()
    assert '-2' == str(err.value)
    out, err = capsys.readouterr()
    assert out.startswith("ERROR: 'current/buildout.cfg' already exists")


def test_update__update__5(basedir):
    """It prints exits if `install.user.ini` doesn't exist."""
    basedir.mkdir(CURRENT_NAME)
    with pytest.raises(IOError) as err:
        update()
    assert str(err.value).endswith("current/install.user.ini' does not exist.")
