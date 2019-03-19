from __future__ import absolute_import

from . import CURRENT_NAME
import os
import os.path


def symlink(dir_name):
    """Create or update the `current` symlink to point to `dir_name`."""
    if os.path.lexists(CURRENT_NAME):
        os.unlink(CURRENT_NAME)
    os.symlink(str(dir_name), CURRENT_NAME)
