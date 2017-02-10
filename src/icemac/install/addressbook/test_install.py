from . import CURRENT_NAME
from install import download_url_and_version, extract_archive_from, install
from install import symlink, main
from install import make_current
import contextlib
import io
import mock
import os.path
import pathlib
import pkg_resources
import pytest
import sys


example_zip_url = pathlib.Path(pkg_resources.resource_filename(
    'icemac.install.addressbook',
    'fixtures/icemac.addressbook-2.0.1.zip')).as_uri()


example_tgz_url = pathlib.Path(pkg_resources.resource_filename(
    'icemac.install.addressbook',
    'fixtures/icemac.addressbook-2.8.tar.gz')).as_uri()


@pytest.fixture('function')
def local_pypi():
    """Patch the call to PyPI to a file URL."""
    url = pathlib.Path(pkg_resources.resource_filename(
        'icemac.install.addressbook',
        'fixtures/icemac.addressbook.json')).as_uri()
    with mock.patch('icemac.install.addressbook.install.PYPI_JSON_URL',
                    new=url):
        yield


def test_update__main__1(local_pypi):
    """It calls some functions with appropriate parameters."""
    path = 'icemac.install.addressbook.install'
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


def test_update__main__2(local_pypi, capsys):
    """It defaults to the newest version."""
    path = 'icemac.install.addressbook.install'
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


def test_update__main__2_5(basedir, capsys):
    """It does not overwrite an existing installation."""
    path = 'icemac.install.addressbook.install'
    extract_archive_from(example_zip_url)
    with mock.patch(path + '.download_url_and_version') as dl_url_and_version,\
            mock.patch(path + '.install') as install:
        dl_url_and_version.return_value = example_zip_url, '2.0.1'
        main(['2.0.1'])
    assert not install.called
    out, err = capsys.readouterr()
    assert [
        u"Downloading version 2.0.1 of icemac.addressbook ...",
        u"'icemac.addressbook-2.0.1' already exists.",
        u""] == out.split("\n")


def test_update__main__3():
    """It drops into pdb on an exception if required."""
    path = 'icemac.install.addressbook.install'
    with mock.patch(path + '.download_url_and_version',
                    side_effect=RuntimeError),\
            mock.patch('pdb.post_mortem') as post_mortem:
        main(['--debug'])
    post_mortem.assert_called_with()


def test_update__main__4():
    """It it raises the exception if debugger is not required."""
    path = 'icemac.install.addressbook.install'
    with mock.patch(path + '.download_url_and_version',
                    side_effect=RuntimeError),\
            pytest.raises(RuntimeError):
        main([])


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


def test_update__download_url_and_version__1(local_pypi):
    """It returns the URL to download the specified address book version."""
    assert ((
        'https://pypi.python.org/packages/dd/01/'
        '36f28ce3db10431ec21245233e6562fc609d8301003b981b28fb3aedcf67/'
        'icemac.addressbook-1.10.5.zip', '1.10.5') ==
        download_url_and_version('1.10.5'))


def test_update__download_url_and_version__2(local_pypi):
    """It raises a ValueError if the specified version does not exist."""
    with pytest.raises(ValueError) as err:
        download_url_and_version('24.11')
    assert "Release '24.11' does not exist." == str(err.value)


def test_update__download_url_and_version__3(local_pypi):
    """It raises a ValueError if the specified version has not sdist."""
    with pytest.raises(ValueError) as err:
        download_url_and_version('1.1.1')
    assert "Release '1.1.1' does not have an sdist release." == str(err.value)


def test_update__download_url_and_version__4(local_pypi):
    """It returns the URL of the newest address book version if ...

    called with `None` as version.
    """
    assert ((
        'https://pypi.python.org/packages/f9/e6/'
        '3b40e95936e32fa3d46cc5807785217c6444c086e669ccffffe0a2dff6ee/'
        'icemac.addressbook-2.8.tar.gz', '2.8') ==
        download_url_and_version(None))


def test_update__extract_archive_from__1(basedir):
    """It downloads a zip file from a url and extracts it to cwd."""
    extract_dir = extract_archive_from(example_zip_url)
    assert 'icemac.addressbook-2.0.1' == extract_dir
    assert {'__init__.py', 'install.py'} == set(os.listdir(extract_dir))


def test_update__extract_archive_from__2(basedir):
    """It downloads a tgz file from a url and extracts it to cwd."""
    extract_dir = extract_archive_from(example_tgz_url)
    assert 'icemac.addressbook-2.8' == extract_dir
    assert {'__init__.py', 'install.py'} == set(os.listdir(extract_dir))


def test_update__extract_archive_from__3(basedir):
    """It raises a RuntimeError if the extract dir already exists."""
    extract_archive_from(example_tgz_url)
    with pytest.raises(RuntimeError) as err:
        extract_archive_from(example_tgz_url)
    assert "'icemac.addressbook-2.8' already exists." == str(err.value)


def test_update__install__1(basedir):
    """It runs the address book installer in the given directory."""
    address_book_dir = extract_archive_from(example_zip_url)
    stdin = io.StringIO()
    with user_input(u'foo', stdin):
        install(address_book_dir, stdin=stdin)
    assert ({'foo', 'install.py', '__init__.py'} ==
            set(os.listdir(address_book_dir)))


def test_update__install__2(basedir):
    """It calls `install.py` with `current` if it exists in cwd."""
    dir_name = str(basedir.mkdir('icemac.addressbook-2.0.2'))
    with mock.patch('icemac.install.addressbook.install.call_cmd') as call_cmd:
        install(dir_name)
        call_cmd.assert_called_with(sys.executable, 'install.py')

        call_cmd.reset_mock()
        basedir.mkdir(CURRENT_NAME)
        install(dir_name)
        call_cmd.assert_called_with(sys.executable, 'install.py', '../current')


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


def test_update__make_current__1(basedir):
    """It updates the `current` symlink to the given address book version."""
    basedir.mkdir('icemac.addressbook-2.1.2')
    basedir.mkdir('icemac.addressbook-2.1.3')
    symlink('2.1.2')
    make_current(['2.1.3'])
    assert os.path.islink(CURRENT_NAME)
    assert os.path.exists(CURRENT_NAME)  # assert the link is not broken
    assert os.path.realpath(CURRENT_NAME).endswith('icemac.addressbook-2.1.3')
