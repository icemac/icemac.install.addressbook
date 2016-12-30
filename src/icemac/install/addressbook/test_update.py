from update import download_url, extract_zipfile, install, CURRENT_NAME
import contextlib
import io
import mock
import os.path
import pkg_resources
import pytest
import sys


@contextlib.contextmanager
def user_input(input, stdin):
    r"""Write `input` on `stdin`.

    Taken from icemac.addressbook + adapted to use it here.
    """
    # Remove possibly existing previous input:
    stdin.seek(0)
    stdin.truncate()
    stdin.write(input)
    stdin.seek(0)
    yield


def test_update__download_url__1():
    """It returns the URL to download the specified address book version."""
    with mock.patch('urllib.urlopen') as urlopen:
        urlopen.return_value = pkg_resources.resource_stream(
            'icemac.install.addressbook', 'fixtures/icemac.addressbook.json')
        assert (
            'https://pypi.python.org/packages/dd/01/'
            '36f28ce3db10431ec21245233e6562fc609d8301003b981b28fb3aedcf67/'
            'icemac.addressbook-1.10.5.zip' == download_url('1.10.5'))


def test_update__download_url__2():
    """It raises a ValueError if the specified version does not exist."""
    with mock.patch('urllib.urlopen') as urlopen:
        urlopen.return_value = pkg_resources.resource_stream(
            'icemac.install.addressbook', 'fixtures/icemac.addressbook.json')
        with pytest.raises(ValueError) as err:
            download_url('24.11')
        assert "Release '24.11' does not exist." == str(err.value)


def test_update__download_url__3():
    """It raises a ValueError if the specified version has not sdist."""
    with mock.patch('urllib.urlopen') as urlopen:
        urlopen.return_value = pkg_resources.resource_stream(
            'icemac.install.addressbook', 'fixtures/icemac.addressbook.json')
        with pytest.raises(ValueError) as err:
            download_url('1.1.1')
        assert ("Release '1.1.1' does not have an sdist release." ==
                str(err.value))


example_zip = pkg_resources.resource_stream(
    'icemac.install.addressbook', 'fixtures/icemac.addressbook-2.0.1.zip')


def test_update__extract_zipfile__1(basedir):
    """It extracts a file like object to a temporary directory."""
    extract_dir = extract_zipfile(example_zip)
    assert 'icemac.addressbook-2.0.1' == extract_dir
    assert {'__init__.py', 'install.py'} == set(os.listdir(extract_dir))


def test_update__install__1(basedir):
    """It runs the address book installer in the given directory."""
    address_book_dir = extract_zipfile(example_zip)
    stdin = io.StringIO()
    with user_input(u'foo', stdin):
        install(address_book_dir, stdin=stdin)
    assert ({'foo', 'install.py', '__init__.py'} ==
            set(os.listdir(address_book_dir)))


def test_update__install__2(basedir):
    """It calls `install.py` with `current` if it exists in cwd."""
    dir_name = str(basedir)
    with mock.patch('icemac.install.addressbook.update.call_cmd') as call_cmd:
        install(dir_name)
        call_cmd.assert_called_with(sys.executable, 'install.py')

        call_cmd.reset_mock()
        basedir.mkdir(CURRENT_NAME)
        install(dir_name)
        call_cmd.assert_called_with(sys.executable, 'install.py', 'current')
