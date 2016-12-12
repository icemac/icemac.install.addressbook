=========================
icemac.update.addressbook
=========================

Scripts to update the installation of `icemac.addressbook`_  to a new version
of the package.

.. _`icemac.addressbook` : https://pypi.org/project/icemac.addressbook/

.. contents::

Copyright
=========

Copyright (c) 2016 Michael Howitz

All Rights Reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.

Prerequisites
=============

The following software needs to be installed to use the scripts provided by
this package:

* ``tar`` with bzip2 support


.. XXX sure about this?


To use the scripts in this package you need an existing installation of `icemac.addressbook`, see Installation_.

.. _Installation : https://bitbucket.org/icemac/icemac.addressbook/wiki/Installation

The `icemac.addressbook` package has to be ...

Installation of the update scripts
==================================

Install the package `icemac.update.addressbook` using pip::

    $ pip install icemac.update.addressbook

This creates two scripts in the `bin` directory:

    * ``update-addressbook``
    * ``archive-addressbook``

Usage
=====

update-addressbook
------------------

Start the script using::

    $ update-addressbook 4.2

Where ``4.2`` is the number of the version you want to install.

The script executes the following steps:

1. Download the source distribution of `icemac.addressbook` to a directory
   named ``sources``.
2. Extract the source distribution to the current working directory.
3. Run the install script. If there is a symlink named ``current`` pointing to
   a previous `icemac.addressbook` installation it uses its
   configuration as default answers for the questions in the installation
   process.
4. Change the target of the symlink named ``current`` to point to the new
   installation.


archive-addressbook
-------------------

Start the script using::

    $ archive-addressbook 4.1

Where ``4.1`` is the version number of the installation you want to archive.

The script executes the following steps:

1. Create a bzipped tar archive (.tar.bz2) of the requested
   `icemac.addressbook` installation (as installed by update-addressbook_) in a
   directory named ``archive``.
2. Delete the requested `icemac.addressbook` installation.



TODO
====

* Prerequisites_ (s. above)
* Trove classifiers
