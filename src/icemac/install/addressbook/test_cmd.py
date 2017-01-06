from .cmd import call_cmd
import pytest


def test_cmd__call_cmd__1(basedir):
    """It calls a command and return nothing."""
    basedir.mkdir('test')
    assert None is call_cmd('tar', '-cjf', 'test.tar.bz2', 'test')
    assert ({'test', 'test.tar.bz2'} ==
            set([x.basename for x in basedir.listdir()]))


def test_cmd__call_cmd__2(basedir):
    """It raises SystemExit on an error."""
    with pytest.raises(SystemExit):
        call_cmd('tar', '-cjf', 'test.tar.bz2', 'test')
