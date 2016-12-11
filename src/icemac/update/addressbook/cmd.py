import sys
import subprocess


def call_cmd(cmd):
    """Call a command provided as string.

    Exit to the shell on failure.
    """
    process = subprocess.Popen(cmd.split())
    if process.wait() != 0:
        sys.exit(-1)
