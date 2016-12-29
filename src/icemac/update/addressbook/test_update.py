from update import download_url, extract_zipfile
import mock
import os.path
import pkg_resources
import pytest


def test_update__download_url__1():
    """It returns the URL to download the specified address book version."""
    with mock.patch('urllib.urlopen') as urlopen:
        urlopen.return_value = pkg_resources.resource_stream(
            'icemac.update.addressbook', 'fixtures/icemac.addressbook.json')
        assert (
            'https://pypi.python.org/packages/dd/01/'
            '36f28ce3db10431ec21245233e6562fc609d8301003b981b28fb3aedcf67/'
            'icemac.addressbook-1.10.5.zip' == download_url('1.10.5'))


def test_update__download_url__2():
    """It raises a ValueError if the specified version does not exist."""
    with mock.patch('urllib.urlopen') as urlopen:
        urlopen.return_value = pkg_resources.resource_stream(
            'icemac.update.addressbook', 'fixtures/icemac.addressbook.json')
        with pytest.raises(ValueError) as err:
            download_url('24.11')
        assert "Release '24.11' does not exist." == str(err.value)


def test_update__download_url__3():
    """It raises a ValueError if the specified version has not sdist."""
    with mock.patch('urllib.urlopen') as urlopen:
        urlopen.return_value = pkg_resources.resource_stream(
            'icemac.update.addressbook', 'fixtures/icemac.addressbook.json')
        with pytest.raises(ValueError) as err:
            download_url('1.1.1')
        assert ("Release '1.1.1' does not have an sdist release." ==
                str(err.value))


def test_update__extract_zipfile__1(basedir):
    """It extracts a file like object to a temporary directory."""
    example_zip = pkg_resources.resource_stream(
        'icemac.update.addressbook', 'fixtures/icemac.addressbook-2.0.1.zip')
    extract_dir = extract_zipfile(example_zip)
    assert 'icemac.addressbook-2.0.1' == extract_dir
    assert ['__init__.py'] == os.listdir(extract_dir)
