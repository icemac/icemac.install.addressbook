from .install.config import USER_INI
import contextlib
import six


@contextlib.contextmanager
def user_input(input, stdin):
    r"""Write `input` on `stdin`.

    If `input` is a list, join it using `\n`.
    """
    # Remove possibly existing previous input:
    stdin.seek(0)
    stdin.truncate()
    if not isinstance(input, six.string_types):
        input = '\n'.join(input)
    stdin.write(input)
    stdin.seek(0)
    yield


def create_script(dir, name):
    """Create a script in `dir` which prints its args."""
    f = dir.join(name)
    f.write('#!/bin/bash\necho $0 $*')
    f.chmod(0o700)


def create_install_default_ini(dir):
    """Create an `install.default.ini` for `Configurator`."""
    install_default_ini = dir.join('install.default.ini')
    install_default_ini.write("""\
[install]
eggs_dir = py-eggs

[admin]
login = me

[server]
host = my.computer.local
port = 13090
username =

[log]
handler = FileHandler
max_size = 1000
when = midnight
interval = 1
backups = 5

[packages]

[migration]
do_migration = no
stop_server = no
start_server = no

[links]
imprint_text = Imprint
imprint_url =
dataprotection_text = Data Protection
dataprotection_url =
""")


def user_ini(basedir, section, **kw):
    """Fill the user_ini with the given section and values."""
    user_ini = basedir.join(USER_INI)
    user_ini.write('[{}]\n'.format(section))
    for key, value in kw.items():
        user_ini.write('{} = {}\n'.format(key, value), mode='a')
