from install import download_url, extract_zipfile_from, install, CURRENT_NAME
from install import symlink, main
import contextlib
import io
import mock
import os.path
import pathlib
import pkg_resources
import pytest
import sys


def test_update__main__1():
    """It calls some functions with appropriate parameters."""
    path = 'icemac.install.addressbook.install'
    with mock.patch(path + '.download_url') as download_url,\
            mock.patch(path + '.extract_zipfile_from') as extract_zipfile,\
            mock.patch(path + '.install') as install,\
            mock.patch(path + '.symlink') as symlink:
        download_url.return_value = 'http://url.to/icemac.addressbook-4.3.zip'
        extract_zipfile.return_value = 'icemac.addressbook-4.3'
        main(['4.3'])
    download_url.assert_called_with('4.3')
    install.assert_called_with('icemac.addressbook-4.3')
    symlink.assert_called_with('icemac.addressbook-4.3')


@contextlib.contextmanager
def user_input(input, stdin):
    """Write `input` on `stdin`.

    Taken from icemac.addressbook + adapted to use it here.
    """
    # Remove possibly existing previous input:
    stdin.seek(0)
    stdin.truncate()
    stdin.write(input)
    stdin.seek(0)
    yield


local_pypi_json_url = pathlib.Path(pkg_resources.resource_filename(
    'icemac.install.addressbook', 'fixtures/icemac.addressbook.json')).as_uri()


def test_update__download_url__1():
    """It returns the URL to download the specified address book version."""
    with mock.patch('icemac.install.addressbook.install.PYPI_JSON_URL',
                    new=local_pypi_json_url):
        assert (
            'https://pypi.python.org/packages/dd/01/'
            '36f28ce3db10431ec21245233e6562fc609d8301003b981b28fb3aedcf67/'
            'icemac.addressbook-1.10.5.zip' == download_url('1.10.5'))


def test_update__download_url__2():
    """It raises a ValueError if the specified version does not exist."""
    with mock.patch('icemac.install.addressbook.install.PYPI_JSON_URL',
                    new=local_pypi_json_url):
        with pytest.raises(ValueError) as err:
            download_url('24.11')
        assert "Release '24.11' does not exist." == str(err.value)


def test_update__download_url__3():
    """It raises a ValueError if the specified version has not sdist."""
    with mock.patch('icemac.install.addressbook.install.PYPI_JSON_URL',
                    new=local_pypi_json_url):
        with pytest.raises(ValueError) as err:
            download_url('1.1.1')
        assert ("Release '1.1.1' does not have an sdist release." ==
                str(err.value))


example_url = pathlib.Path(pkg_resources.resource_filename(
    'icemac.install.addressbook',
    'fixtures/icemac.addressbook-2.0.1.zip')).as_uri()


def test_update__extract_zipfile_from__1(basedir):
    """It extracts a file like object to a temporary directory."""
    extract_dir = extract_zipfile_from(example_url)
    assert 'icemac.addressbook-2.0.1' == extract_dir
    assert {'__init__.py', 'install.py'} == set(os.listdir(extract_dir))


def test_update__install__1(basedir):
    """It runs the address book installer in the given directory."""
    address_book_dir = extract_zipfile_from(example_url)
    stdin = io.StringIO()
    with user_input(u'foo', stdin):
        install(address_book_dir, stdin=stdin)
    assert ({'foo', 'install.py', '__init__.py'} ==
            set(os.listdir(address_book_dir)))


def test_update__install__2(basedir):
    """It calls `install.py` with `current` if it exists in cwd."""
    dir_name = str(basedir)
    with mock.patch('icemac.install.addressbook.install.call_cmd') as call_cmd:
        install(dir_name)
        call_cmd.assert_called_with(sys.executable, 'install.py')

        call_cmd.reset_mock()
        basedir.mkdir(CURRENT_NAME)
        install(dir_name)
        call_cmd.assert_called_with(sys.executable, 'install.py', 'current')


def test_update__symlink__1(basedir):
    """It creates a symlink named `current` to the given directory."""
    basedir.mkdir('icemac.addressbook-2.1.2')
    symlink('icemac.addressbook-2.1.2')
    assert os.path.islink(CURRENT_NAME)
    assert os.path.exists(CURRENT_NAME)  # assert the link is not broken
    assert os.path.realpath(CURRENT_NAME).endswith('icemac.addressbook-2.1.2')


def test_update__symlink__2(basedir):
    """It replaces an existing symlink."""
    basedir.mkdir('icemac.addressbook-2.1.2')
    basedir.mkdir('icemac.addressbook-2.1.3')
    symlink('icemac.addressbook-2.1.2')
    symlink('icemac.addressbook-2.1.3')
    assert os.path.islink(CURRENT_NAME)
    assert os.path.exists(CURRENT_NAME)  # assert the link is not broken
    assert os.path.realpath(CURRENT_NAME).endswith('icemac.addressbook-2.1.3')
