import sys
import subprocess


def call_cmd(text, *cmd_parts, **kw):
    """Render ``text`` and call a command provided as arguments.

    Exit to the shell on failure.
    """
    print('{} ...'.format(text))
    process = subprocess.Popen(cmd_parts, **kw)
    if process.wait() != 0:
        sys.exit(-1)
