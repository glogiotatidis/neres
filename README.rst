NewRelic Synthetics (unofficial) CLI (NeReS)
============================================

|image0| |image1| |image2|

NeReS is a cli tool to manage `NewRelic Synthetics
<https://synthetics.newrelic.com/>`__ monitors with a Synthetics Lite account
(Pro should work too). The tool emulates the actions of a user in the browser
and doesn't use the Synthetics API since that's only available to the Pro
accounts.

Use the tools you can:

-  List all your monitors, including their success rate, locations,
   notifications etc.
-  Create, update and delete monitors
-  List available locations for monitor installation

Everything you can do using the Web console is supported and provided to your
shell prompt.

Installation
------------

.. code:: shell

   $ pip install neres



Configuration
-------------

1. You will need a newrelic account
2. Start by using the `login` command
3. Read the docs or run `--help`


Use
---

Login to NewRelic
~~~~~~~~~~~~~~~~~~

Login to NewRelic with the `login` command:

.. code:: shell

   $ neres login

If you have multiple NewRelic accounts you can have different environments:

.. code:: shell

   $ neres --environment work login

.. note::

  Default environment is named `newrelic`. Remember to always pass `--environment`
  to all neres commands to execute them in the correct environment. Alternatively
  you can add `NERES_ENVIRONMENT` to your environment variables list.


List Accounts
~~~~~~~~~~~~~

You can list all the accounts connected to the email you used to connect using:

.. code:: shell

   $ neres list-accounts

By default neres will act on the first account listed. This command will help
you select a different account by using the `ID` of the account in combination
with the `--account` option or by setting `NERES_ACCOUNT` in your environment.

List Locations
~~~~~~~~~~~~~~

Lists available monitor locations:

.. code:: shell

   $ neres list-locations

List Monitors
~~~~~~~~~~~~~

Lists available monitors:

.. code:: shell

   $ neres list-monitors

You can only list IDs of the monitors:

.. code:: shell

   $ neres list-monitors --ids-only

Or get the raw JSON output from NewRelic:

.. code:: shell

   $ neres list-monitors --raw

Add Monitor
~~~~~~~~~~~

Adds a Synthetics monitor:

.. code:: shell

   $ neres add-monitor monitorName http://example.com

Use `--help` to get a full list of supported options for the command. All
options are optional.


Get Monitor
~~~~~~~~~~~

Get details on a monitor

.. code:: shell

   $ neres get-monitor de310b69-3195-435e-b1ef-3a0af67499de


.. note::

   You can use `list-monitors` to get a list of available monitors.

Update Monitor
~~~~~~~~~~~~~~

Update an existing monitor

.. code:: shell

   $ neres update-monitor de310b69-3195-435e-b1ef-3a0af67499de --name "Foobar"

Use `--help` to get a full list of supported options for the command. All
options are optional.


Open Monitor
~~~~~~~~~~~~

Open monitor in the browser

.. code:: shell

   $ neres open de310b69-3195-435e-b1ef-3a0af67499de

Credits
-------

This package was created with
`Cookiecutter <https://github.com/audreyr/cookiecutter>`__ and the
`audreyr/cookiecutter-pypackage <https://github.com/audreyr/cookiecutter-pypackage>`__
project template.

.. |image0| image:: https://img.shields.io/pypi/v/neres.svg
.. |image1| image:: https://travis-ci.org/glogiotatidis/neres.svg?branch=master
.. |image2| image:: https://pyup.io/repos/github/glogiotatidis/neres/shield.svg
