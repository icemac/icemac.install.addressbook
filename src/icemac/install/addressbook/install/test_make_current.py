from __future__ import absolute_import

from .. import CURRENT_NAME
from .make_current import main
from ..utils import symlink
import os.path


def test_make_current__main__1(basedir):
    """It updates the `current` symlink to the given address book version."""
    basedir.mkdir('icemac.addressbook-2.1.2')
    basedir.mkdir('icemac.addressbook-2.1.3')
    symlink('2.1.2')
    main(['2.1.3'])
    assert os.path.islink(CURRENT_NAME)
    assert os.path.exists(CURRENT_NAME)  # assert the link is not broken
    assert os.path.realpath(CURRENT_NAME).endswith('icemac.addressbook-2.1.3')
