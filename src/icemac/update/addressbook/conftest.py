import pytest


@pytest.fixture('function')
def basedir(tmpdir):
    """Create a base directory for the tests and chdir to it."""
    tmpdir.chdir()
    yield tmpdir
