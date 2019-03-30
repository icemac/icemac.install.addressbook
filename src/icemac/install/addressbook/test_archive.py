from .archive import main, prepare_archive, archive, ARCHIVE_DIR_NAME
from .install.install import symlink
from icemac.install.addressbook._compat import Path
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


def test_archive__main__1(address_book, capsys):
    """It archives the specified address book version."""
    main(['24.11'])
    out, err = capsys.readouterr()
    assert [
        'Archiving icemac.addressbook-24.11 ...',
        'Done archiving to archive/icemac.addressbook-24.11.tar.bz2.',
    ] == out.splitlines()
    assert '' == err


def test_archive__prepare_archive__1():
    """It raises a ValueError if the file does not exist."""
    with pytest.raises(ValueError) as err:
        prepare_archive('24.11')
    assert ("Directory 'icemac.addressbook-24.11' does not exist." ==
            str(err.value))


def test_archive__prepare_archive__2(address_book):
    """It creates the archive directory if it does not exist."""
    prepare_archive('24.11')
    assert 'archive' in [x.basename for x in address_book.listdir()]


def test_archive__prepare_archive__3(address_book, archive_dir):
    """It returns the file name to be archived and the format."""
    assert ((Path('icemac.addressbook-24.11'), 'bztar')
            == prepare_archive('24.11'))


def test_archive__prepare_archive__4(address_book, archive_dir):
    """It refuses to archive the current version."""
    symlink('icemac.addressbook-24.11')
    with pytest.raises(AssertionError) as err:
        prepare_archive('24.11')
    assert ("'icemac.addressbook-24.11' is the current address book -- "
            "cannot archive it!" == str(err.value))


def test_archive__archive__1(address_book, archive_dir):
    """It archives the address book and deletes it."""
    result = archive('icemac.addressbook-24.11', 'bztar')
    assert (
        ['icemac.addressbook-24.11.tar.bz2'] ==
        [x.basename for x in address_book.join(ARCHIVE_DIR_NAME).listdir()])
    assert ['archive'] == [x.basename for x in address_book.listdir()]
    assert ('Done archiving to archive/icemac.addressbook-24.11.tar.bz2.' ==
            result)
