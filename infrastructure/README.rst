.. image:: https://img.shields.io/badge/license-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl.html
   :alt: License: LGPL-3

=============================
Base Infrastructure Connector
=============================

Adds models and central mechanisms for connecting to infrastructure services.

Installation
============


Configuration
=============

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/10.0

Known Issues / Roadmap
======================

Known Issues
------------

* Kernel name is hard coded to Linux. This poses obvious data issues with Windows
  hosts, but is purely visual.
* CPU count and pin in infrastructure service config are not compatible with each
  other. This can be fixed for the most part by adding a parser for the pinning.

Road Map
--------

* Provide real permissions.
* Add the ability to track licenses that are actually being used against the
  host or service that is using them.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues 
<https://github.com/LasLabs/odoo-connector-rancher/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first, 
help us smash it by providing detailed and welcomed feedback.


Credits
=======

Contributors
------------

* Dave Lasley <dave@laslabs.com>

Do not contact contributors directly about support or help with technical issues.

Maintainer
----------

.. image:: https://laslabs.com/logo.png
   :alt: LasLabs Inc.
   :target: https://laslabs.com

This module is maintained by LasLabs Inc.
