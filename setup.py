"""poor man's integration testing"""

from setuptools import setup, find_packages


setup(
    name='icemac.update.addressbook',
    version='1.0.dev0',

    install_requires=[
    ],

    extras_require={
        'test': [],
    },

    entry_points={
        'console_scripts': [
            'update-addressbook = icemac.update.addressbook.update:main',
            'archive-addressbook = icemac.update.addressbook.archive:main',
        ],
    },

    author='Michael Howitz',
    author_email='icemac@gmx.net',
    license='ZPL 2.1',
    url='https://bitbucket.org/icemac/icemac.update.addressbook/',

    keywords='icemac addressbook install update',
    classifiers="""\
Development Status :: 4 - Beta
Environment :: Console
License :: OSI Approved
License :: OSI Approved :: Zope Public License
Natural Language :: English
Operating System :: OS Independent
Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 2.7
Programming Language :: Python :: Implementation
Programming Language :: Python :: Implementation :: CPython
Topic :: Utilities
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
