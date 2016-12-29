import os
import pytest


@pytest.fixture('function')
def basedir(tmpdir):
    """Create a base directory for the tests and chdir to it."""
    cwd = os.getcwd()
    tmpdir.chdir()
    yield tmpdir
    os.chdir(cwd)
