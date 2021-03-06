from __future__ import absolute_import, print_function
import configparser
import shutil
import sys
import zope.password.password


INDEX_URL = "https://pypi.python.org/simple"
USER_INI = "install.user.ini"


class Configurator(object):
    """Configure installation.

    user_config ... pathlib.Path to config file with previously entered user
                    values which take precedence over application defaults.
                    Might be None, so no user values are used.
    install_new_version ... If true install a new version otherwise only update
                            the existing configuration.
    stdin ... If not `None` use this stream instead of `sys.stdin`.
    """

    salt = None  # means: use random salt
    force_new_password = False

    def __init__(
            self, user_config=None, install_new_version=True, stdin=None):
        self.user_config = user_config
        self.install_new_version = install_new_version
        if stdin is not None:
            self.stdin = stdin
        else:
            self.stdin = sys.stdin

    def __call__(self):
        self.load()
        self.print_intro()
        self.get_global_options()
        self.get_server_options()
        self.get_log_options()
        self.get_imprint_link_config()
        self.get_data_protection_link_config()
        self.print_additional_packages_intro()
        self.get_additional_packages()
        if self.install_new_version:
            self.get_migration_options()
        else:
            self.get_restart_options()
        self.create_admin_zcml()
        self.create_buildout_cfg()
        self.store()
        return True

    @property
    def first_time_installation(self):
        """Return whether the address book is installed for the first time.

        This means we do not need a migration but an admin password.
        """
        return not(self.user_config)

    def ask_user(
            self, question, section, option, global_default=None, values=(),
            store_in_config=True, required=False):
        """Ask the user for a value of section/option and store it in config.

        global_default ... use this value as default value when it is not
                           defined in the global config file
        values ... when set, only this value can be entered
        store_in_config ... boolean telling whether the value entered by the
                            user should be stored in the config file as default
                            value for the installation of an address book
                            upgrade
        required ... it is required to enter a value
        """
        try:
            default = self.get(section, option)
        except configparser.NoOptionError:
            assert global_default is not None
            default = global_default
        while True:
            print(' {question}: [{default}] '.format(
                question=question, default=default), end='')
            got = self.stdin.readline().strip()
            print()
            if not got:
                got = default
            if required and not got:
                print('ERROR: You have to enter a value.')
                continue
            if not values or got in values:
                break
            else:
                print('ERROR: %r is not in %r.' % (got, values))
                print('Please choose a value out of the list.')
        if store_in_config:
            self._conf.set(section, option, got)
        return got

    def get(self, section, key):
        return self._conf.get(section, key)

    def load(self):
        """Load the configuration from file.

        Default configuration is always read and user configuration is
        read when `user_config` is set on instance.

        """
        if (self.user_config is not None and not self.user_config.exists()):
            raise IOError("'%s' does not exist." % self.user_config)

        to_read = ['install.default.ini']
        if self.user_config is not None:
            to_read.append(str(self.user_config))  # PY2: Remove str later on 3

        # create config
        self._conf = configparser.ConfigParser()
        self._conf.read(to_read)
        if self.install_new_version:
            if self.user_config is not None:
                self._conf.set(
                    'migration', 'old_instance', str(self.user_config.parent))
            else:
                self._conf.set('migration', 'old_instance', '')
        # If there is an existing password force to set a new one which will
        # be encrypted:
        self.force_new_password = self._conf.remove_option('admin', 'password')

    def print_intro(self):
        if self.install_new_version:
            print('Welcome to icemac.addressbook installation')
        else:
            print('Welcome to changing your icemac.addressbook installation')
        print()
        print('Hint: to use the default value (the one in [brackets]), '
              'enter no value.')
        print()

    def get_global_options(self):
        self.eggs_dir = self.ask_user(
            'Directory to store python eggs', 'install', 'eggs_dir')

    def get_server_options(self):
        self.admin_login = self.ask_user(
            'Log-in name for the administrator', 'admin', 'login')
        if self.first_time_installation or self.force_new_password:
            self.admin_passwd = self.ask_user(
                'Password for the administrator', 'admin', 'password',
                global_default='', store_in_config=False, required=True)
        else:
            self.admin_passwd = self.ask_user(
                'New password for the administrator (only enter a value if you'
                ' want to change the existing password)', 'admin', 'password',
                global_default='', store_in_config=False)
        self.host = self.ask_user('Hostname', 'server', 'host')
        self.port = self.ask_user('Port number', 'server', 'port')
        self.username = self.ask_user(
            'Username whether process should run as different user otherwise '
            'emtpy', 'server', 'username')

    def get_log_options(self):
        print(' Please choose Log-Handler:')
        print('    Details see '
              'http://docs.python.org/library/logging.html#handler-objects')
        handlers = (
            'FileHandler', 'RotatingFileHandler', 'TimedRotatingFileHandler')
        log_handler = None
        log_handler = self.ask_user(
            'Log-Handler, choose between ' + ', '.join(handlers),
            'log', 'handler', values=handlers)
        if log_handler == 'RotatingFileHandler':
            self.log_max_bytes = self.ask_user(
                'Maximum file size before rotating in bytes',
                'log', 'max_size')
        elif log_handler == 'TimedRotatingFileHandler':
            self.log_when = self.ask_user(
                'Type of rotation interval, choose between S, M, H, D, W, '
                'midnight', 'log', 'when',
                values=('S', 'M', 'H', 'D', 'W', 'midnight'))
            self.log_interval = self.ask_user(
                'Rotation interval size', 'log', 'interval')
        if log_handler in ('RotatingFileHandler', 'TimedRotatingFileHandler'):
            self.log_backups = self.ask_user(
                'Number of log file backups', 'log', 'backups')
        self.log_handler = log_handler

    def get_imprint_link_config(self):
        print(' Configuration of the imprint link. It is shown in the footer'
              ' of each page. (Leave empty to omit the link.)')
        self.imprint_url = self.ask_user('URL', 'links', 'imprint_url')
        self.imprint_text = self.ask_user('Link text', 'links', 'imprint_text')

    def get_data_protection_link_config(self):
        print(' Configuration of the data protection link. It is shown in the '
              ' footer of each page. (Leave empty to omit the link.)')
        self.dataprotection_url = self.ask_user(
            'URL', 'links', 'dataprotection_url')
        self.dataprotection_text = self.ask_user(
            'Link text', 'links', 'dataprotection_text')

    def print_additional_packages_intro(self):
        print(' When you need additional packages (e. g. import readers)')
        print(' enter the package names here separated by a newline.')
        print(' When you are done enter an empty line.')
        print(' Known packages:')
        print('   icemac.ab.importer -- Import of CSV files')
        print('   icemac.ab.importxls -- Import of XLS (Excel) files')
        print(
            '   icemac.ab.calendar -- Calendar using persons in address book')

    def get_additional_packages(self):
        packages = []
        index = 1
        while True:
            package = self.ask_user(
                'Package %s' % index, 'packages', 'package_%s' % index,
                global_default='')
            index += 1
            if not package:
                break
            packages.append(package)
        self.packages = packages

    def get_migration_options(self):
        if self.first_time_installation:
            self._conf.set('migration', 'do_migration', 'no')
            return
        yes_no = ('yes', 'no')
        self.do_migration = self.ask_user(
            ' Migrate old address book content to new instance', 'migration',
            'do_migration', values=yes_no)
        if self.do_migration == 'no':
            return
        print('The old address book instance must not run during migration.')
        print('When it runs as demon process the migration script can stop it '
              'otherwise you have to stop it manually.')
        self.stop_server = self.ask_user(
            'Old instance is running as a demon process', 'migration',
            'stop_server', values=yes_no)
        self.start_server = self.ask_user(
            'New instance should be started as a demon process after '
            'migration', 'migration', 'start_server', values=yes_no)

    def get_restart_options(self):
        print('The address book instance has to be restarted.')
        print('When it runs as demon process it can be restarted'
              ' automatically otherwise you have to restart it manually.')
        self.restart_server = self.ask_user(
            'Should the instance be automatically restarted?',
            'migration', '', values=('yes', 'no'), store_in_config=False,
            global_default='yes')

    def create_admin_zcml(self):
        if self.admin_passwd:
            self._write_new_admin_zcml()
        elif self.install_new_version:
            self._copy_old_admin_zcml()

    def create_buildout_cfg(self):
        print('creating buildout.cfg ...')
        buildout_cfg = configparser.ConfigParser()
        buildout_cfg.add_section('buildout')
        buildout_cfg.set('buildout', 'extends', 'profiles/prod.cfg')
        buildout_cfg.set('buildout', 'newest', 'true')
        buildout_cfg.set('buildout', 'allow-picked-versions', 'true')
        buildout_cfg.set('buildout', 'eggs-directory', self.eggs_dir)
        buildout_cfg.set('buildout', 'index', INDEX_URL)
        buildout_cfg.add_section('deploy.ini')
        buildout_cfg.set('deploy.ini', 'host', self.host)
        buildout_cfg.set('deploy.ini', 'port', self.port)
        if self.username:
            buildout_cfg.add_section('zdaemon.conf')
            buildout_cfg.set('zdaemon.conf', 'user', 'user %s' % self.username)
        log_handler = self.log_handler
        if log_handler == 'FileHandler':
            b_log_handler = log_handler
        else:
            # Argh, all other log handlers live in a subpackage
            b_log_handler = 'handlers.' + log_handler
        buildout_cfg.set('deploy.ini', 'log-handler', b_log_handler)
        log_args = getattr(self, '_log_args_{}'.format(log_handler))
        buildout_cfg.set('deploy.ini', 'log-handler-args', log_args)

        if self.packages:
            buildout_cfg.add_section('site.zcml')
            permissions_zcml = (
                '<include package="' +
                '" />\n<include package="'.join(self.packages) +
                '" />')
            buildout_cfg.set('site.zcml', 'permissions_zcml', permissions_zcml)

        with open('buildout.cfg', 'w') as buildout_cfg_file:
            buildout_cfg.write(buildout_cfg_file)
            buildout_cfg_file.write('[app]\n')
            attrs = (
                'imprint_text',
                'imprint_url',
                'dataprotection_text',
                'dataprotection_url',
            )
            buildout_cfg_file.write('initialization += ')
            buildout_cfg_file.write(
                '\n    '.join(
                    'os.environ["AB_LINK_{0}"] = "{1}"'.format(
                        x.upper(), getattr(self, x))
                    for x in attrs
                ))

            if self.packages:
                # configparser can't write '+=' instead of '='
                eggs = '\neggs += %s\n\n' % '\n    '.join(self.packages)
                buildout_cfg_file.write(eggs)
                buildout_cfg_file.write('[test]')
                buildout_cfg_file.write(eggs)

    def store(self):
        print('saving config ...')
        with open(USER_INI, 'w') as user_conf:
            self._conf.write(user_conf)

    @property
    def _log_args_FileHandler(self):
        return "'a'"

    @property
    def _log_args_RotatingFileHandler(self):
        return ', '.join(("'a'", self.log_max_bytes, self.log_backups))

    @property
    def _log_args_TimedRotatingFileHandler(self):
        log_when = "'%s'" % self.log_when
        return ', '.join((log_when, self.log_interval, self.log_backups))

    def _write_new_admin_zcml(self):
        manager = zope.password.password.SSHAPasswordManager()
        password = manager.encodePassword(self.admin_passwd, salt=self.salt)
        print('creating admin.zcml ...')
        with open('admin.zcml', 'w') as admin_zcml:
            admin_zcml.write('\n'.join(
                ('<configure xmlns="http://namespaces.zope.org/zope">',
                 '  <principal',
                 '    id="icemac.addressbook.global.Administrator"',
                 '    title="global administrator"',
                 '    login="%s"' % self.admin_login,
                 '    password_manager="SSHA"',
                 '    password="%s" />' % password,
                 '  <grant',
                 '    role="icemac.addressbook.global.Administrator"',
                 '    principal="icemac.addressbook.global.Administrator" />',
                 '  <grant',
                 '    permission="zope.ManageContent"',
                 '    principal="icemac.addressbook.global.Administrator" />',
                 '</configure>',
                 )))

    def _copy_old_admin_zcml(self):
        print('copying admin.zcml ...')
        shutil.copy2(str(self.user_config.parent / 'admin.zcml'), '.')
