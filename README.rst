.. image:: ../../../badges/master/pipeline.svg
   :target: ../../../-/commits/master
   :alt: pipeline status

.. image:: ../../../badges/master/coverage.svg
   :target: ../../../-/commits/master
   :alt: coverage report


============
Team Project
============

A Python Team Project.


Getting started
===============

Setup
-----

Clone the repository and setup your local checkout:

.. code-block:: bash

   python -m venv venv
   . venv/bin/activate
   
   pip install -r requirements-dev.txt
   pip install -e .
   python -m spacy download en_core_web_md 

This creates a new virtual environment with the necessary python dependencies and installs the project in editable mode.

Run tests
---------

The project uses pytest as its test runner, run the testsuite by simply invoking ``pytest``.

Build documentation
-------------------

Documentation is written with sphinx, to build the documentation from its source run sphinx-build:

.. code-block:: bash

   sphinx-build -a docs public

The entrypoint to the local documentation build should be available under ``public/index.html``.

Add project dependencies
------------------------

Project dependencies are managed via the ``install_requires`` key in ``setup.cfg``. After editing setup.cfg, ``requirements.txt`` needs to be regenerated.

.. code-block:: bash

   pip install pip-tools
   pip-compile --generate-hashes setup.cfg

