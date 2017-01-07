==========================
icemac.install.addressbook
==========================

Scripts to ease the installation and update an existing installation of
`icemac.addressbook`_  to a new version of the package.

.. _`icemac.addressbook` : https://pypi.org/project/icemac.addressbook/

.. contents::

Copyright
=========

Copyright (c) 2016-2017 Michael Howitz

All Rights Reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.


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
4. Create a new symlink named ``current`` pointing to the new installation.


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
