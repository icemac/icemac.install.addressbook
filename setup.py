"""Install, update and archive installations of icemac.addressbook."""

from setuptools import setup, find_packages


setup(
    name='icemac.install.addressbook',
    version='1.0.dev0',

    install_requires=[
    ],

    extras_require={
        'test': [
            'mock',
        ],
    },

    entry_points={
        'console_scripts': [
            'install-addressbook = icemac.install.addressbook.install:main',
            'archive-addressbook = icemac.install.addressbook.archive:main',
        ],
    },

    author='Michael Howitz',
    author_email='icemac@gmx.net',
    license='ZPL 2.1',
    url='https://github.com/icemac/icemac.install.addressbook',

    keywords='icemac addressbook install update archive manage',
    classifiers="""\
Development Status :: 4 - Beta
Environment :: Console
Intended Audience :: System Administrators
License :: OSI Approved
License :: OSI Approved :: Zope Public License
Natural Language :: English
Operating System :: OS Independent
Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 2.7
Programming Language :: Python :: 2 :: Only
Programming Language :: Python :: Implementation
Programming Language :: Python :: Implementation :: CPython
Topic :: System
Topic :: System :: Archiving
Topic :: System :: Installation/Setup
"""[:-1].split('\n'),
    description=__doc__.strip(),
    long_description='\n\n'.join(open(name).read() for name in (
        'README.rst',
        'COPYRIGHT.txt',
        'CHANGES.rst',
    )),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
)
