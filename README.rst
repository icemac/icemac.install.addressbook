==========================
icemac.install.addressbook
==========================

Scripts to ease the installation and update an existing installation of
`icemac.addressbook`_  to a new version of the package.

.. _`icemac.addressbook` : https://pypi.org/project/icemac.addressbook/

.. contents::

Copyright
=========

Copyright (c) 2016-2020 Michael Howitz

This package is licensed under the MIT License, see LICENSE.txt inside the
package.

Installation of the scripts
===========================

Install the package `icemac.install.addressbook` using pip::

    $ pip install icemac.install.addressbook

This creates two scripts in the `bin` directory:

    * ``install-addressbook``
    * ``archive-addressbook``

Usage
=====

install-addressbook
-------------------

Start the script using::

    $ bin/install-addressbook [VERSION_NUMBER]

Where ``VERSION_NUMBER`` is the number of the version you want to install resp.
you want to update to. If you leave it out the newest version is used.


The script executes the following steps:

1. Download the source distribution of `icemac.addressbook` to a temporary
   directory.
2. Extract the source distribution to the current working directory.
3. Run the install script. If there is a symlink named ``current`` pointing to
   a previous `icemac.addressbook` installation it uses its
   configuration as default answers for the questions in the installation
   process.
4. Create or replace the new symlink named ``current`` pointing to the new
   installation.


make-current-addressbook
------------------------

This script is helpful if you want to switch back to an older installed address
book version in case of an error.

Start the script using::

    $ bin/make-current-addressbook VERSION_NUMBER

Where ``VERSION_NUMBER`` is the number of the version you want to make the
current one.

The script executes the following steps:

1. Create or replace the new symlink named ``current`` pointing to the new
   installation.


archive-addressbook
-------------------

After installing a new version of the address book you could archive the
previous one using this script.

Start the script using::

    $ bin/archive-addressbook 4.1

Where ``4.1`` is the version number of the installation you want to archive.

The script executes the following steps:

1. Create an archive of the requested
   `icemac.addressbook` installation (as installed by install-addressbook_) in
   a directory named ``archive``. (The ``archive`` directory is created if it
   not yet exists.)
2. Delete the requested `icemac.addressbook` installation.


change-addressbook-config
-------------------------

If you want change some answers to the questions asked during the installation,
you can run this script.

Start the script using::

    $ bin/change-addressbook-config

The script executes the following steps:

1. The configuration questions get re-presented to you with your previously
   entered values as defaults.

2. The address book instance has to be restarted afterwards. This can be done
   automatically by the script or manually.

Hacking
=======

* Clone the repository::

  $ git clone https://github.com/icemac/icemac.install.addressbook

* Create a virtualenv, install the installer and run it::

  $ cd icemac.install.addressbook
  $ virtualenv-2.7 .
  $ bin/pip install zc.buildout
  $ bin/buildout -n
