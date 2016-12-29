import zipfile
import json
import urllib


PYPI_JSON_URL = (
    'https://pypi.python.org/simple/icemac.addressbook/json')


def download_url(version):
    """Get the download_url."""
    with urllib.urlopen(PYPI_JSON_URL.format(version)) as f:
        data = json.load(f)
    releases = data['releases']
    try:
        packages = releases[version]
    except KeyError:
        raise ValueError('Release {!r} does not exist.'.format(version))
    for package in packages:
        if package['packagetype'] == 'sdist':
            return package['url']
    raise ValueError(
        'Release {!r} does not have an sdist release.'.format(version))


def extract_zipfile(file):
    """Extract a file object as a zip file to a temporary directory.

    Returns the path to the extraction directory.
    """
    with zipfile.ZipFile(file) as zip_file:
        zip_file.extractall()
        return zip_file.namelist()[0].strip('/')
