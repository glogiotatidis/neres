NewRelic Synthetics (unofficial) CLI (NeReS)
============================================

|image0| |image1| |image2|

NeReS is a cli tool to manage `NewRelic
Synthetics <https://synthetics.newrelic.com/>`__ monitors with a
Synthetics Lite account. The tool emulates the actions of a user in the
browser and doesn't use the Synthetics API since that's only available
to the Pro accounts.

Use the tools you can:

-  List all your monitors, including their success rate, locations,
   notifications etc.
-  Create, update and delete monitors
-  List available locations for monitor installation

Everything you can do in the Web is supported and provided to your shell
prompt.

Configuration
-------------

1. You will need a newrelic account
2. Setup in your environment the following variables:

-  ``NERES_ACCOUNT``: Get the number from the URL after you login to NR.
-  ``NERES_EMAIL``: The email you use to login.
-  ``NERES_PASSWORD``: The password you use to login.

or directly provide them when you run the tool.

Commands
--------

-  ``add-monitor``: Creates a monitor
-  ``delete-monitor``: Delete a monitor
-  ``get-monitor``: Get details on a monitor
-  ``list-locations``: Lists available locations to install monitors to
-  ``list-monitors``: Lists all monitors
-  ``open``: The monitor webpage in the browser
-  ``update-monitor``: Updates a monitor

Examples
--------

.. code:: shell

    $ NERES_ACCOUNT=11111 NERES_EMAIL=foo@example.com NERES_PASSWORD=123123 neres list-monitors

TODOS
-----

-  Configuration wizard

Credits
-------

This package was created with
`Cookiecutter <https://github.com/audreyr/cookiecutter>`__ and the
`audreyr/cookiecutter-pypackage <https://github.com/audreyr/cookiecutter-pypackage>`__
project template.

.. |image0| image:: https://img.shields.io/pypi/v/neres.svg
.. |image1| image:: https://travis-ci.org/glogiotatidis/neres.svg?branch=master
.. |image2| image:: https://pyup.io/repos/github/glogiotatidis/neres/shield.svg

