"""Install, update and archive installations of icemac.addressbook."""

from setuptools import setup, find_packages


setup(
    name='icemac.install.addressbook',
    version='1.5.3',

    install_requires=[
        'archive',
        'configparser;python_version<"3"',
        'pathlib2;python_version<"3"',
        'requests',
        'z3c.recipe.usercrontab',
        'zc.buildout',  # `bin/buildout` is needed to install the address book.
        'zc.lockfile',  # this is needed here because it cannot be loaded from
                        # a buildout if zc.buildout is installed via pip.
        'zope.password',
        'zipp < 2',  # keep supporting PY2
    ],

    extras_require={
        'test': [
            'mock < 4',  # keep supporting PY2
            'requests-file',
        ],
    },

    entry_points={
        'console_scripts': [
            'install-addressbook = icemac.install.addressbook.install.install:main',  # noqa: E501
            'make-current-addressbook = icemac.install.addressbook.install.make_current:main',  # noqa: E501
            'change-addressbook-config = icemac.install.addressbook.install.update:main',  # noqa: E501
            'archive-addressbook = icemac.install.addressbook.archive:main',
        ],
    },

    author='Michael Howitz',
    author_email='icemac@gmx.net',
    license='MIT',
    url='https://github.com/icemac/icemac.install.addressbook',

    keywords='icemac addressbook install update archive manage',
    classifiers="""\
Development Status :: 5 - Production/Stable
Environment :: Console
Intended Audience :: System Administrators
License :: OSI Approved :: MIT License
Natural Language :: English
Operating System :: OS Independent
Programming Language :: Python :: 2
Programming Language :: Python :: 2.7
Programming Language :: Python :: 2 :: Only
Programming Language :: Python :: Implementation :: CPython
Topic :: System :: Archiving
Topic :: System :: Installation/Setup
"""[:-1].split('\n'),
    description=__doc__.strip(),
    long_description='\n\n'.join(open(name).read() for name in (
        'README.rst',
        'CHANGES.rst',
    )),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
)
