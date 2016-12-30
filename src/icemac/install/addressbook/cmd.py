import sys
import subprocess


def call_cmd(*cmd_parts, **kw):
    """Call a command provided as arguments.

    Exit to the shell on failure.
    """
    process = subprocess.Popen(cmd_parts, **kw)
    if process.wait() != 0:
        sys.exit(-1)
