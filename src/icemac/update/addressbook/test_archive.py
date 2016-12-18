from .archive import main, archive, ARCHIVE_DIR_NAME
import mock
import pytest


@pytest.fixture('function')
def address_book(basedir):
    """Create a mock address book installation."""
    address_book = basedir.mkdir('icemac.addressbook-24.11')
    address_book.join('README.rst').write('Address book!')
    yield basedir


@pytest.fixture('function')
def archive_dir(basedir):
    """Create an archive directory in the base directory."""
    basedir.mkdir(ARCHIVE_DIR_NAME)


def test_archive__main__1():
    """It calls `archive` with the requested version number."""
    with mock.patch('icemac.update.addressbook.archive.archive') as archive:
        main(['4.3'])
    archive.assert_called_with('4.3')


def test_archive__archive__1():
    """It raises a ValueError if the file does not exist."""
    with pytest.raises(ValueError) as err:
        archive('24.11')
    assert ("Directory 'icemac.addressbook-24.11' does not exist." ==
            str(err.value))


def test_archive__archive__2(address_book):
    """It creates the archive directory if it does not exist."""
    archive('24.11')
    assert 'archive' in [x.basename for x in address_book.listdir()]


def test_archive__archive__3(address_book, archive_dir):
    """It archives the address book and deletes it."""
    result = archive('24.11')
    assert (
        ['icemac.addressbook-24.11.tar.bz2'] ==
        [x.basename for x in address_book.join(ARCHIVE_DIR_NAME).listdir()])
    assert ['archive'] == [x.basename for x in address_book.listdir()]
    assert ('icemac.addressbook-24.11 archived to '
            'archive/icemac.addressbook-24.11.tar.bz2' == result)
