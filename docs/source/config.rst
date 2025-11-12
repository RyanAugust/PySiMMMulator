.. toctree::
   :maxdepth: 2

Configuration
=============

Handlers
--------

Handlers provide a framework for specifiying the inputs to a simulation, critically providing validation checks for each handler that will notify the user if inputs validate global tolerances.

.. automodule:: pysimmmulator.param_handlers
    :members:
    :undoc-members:

Loaders
-------

Functions which automate steps within the parameter workflow. Most notably providing a load from file option `load_config` as well as a comprehensive validation function `validate_config`.

.. automodule:: pysimmmulator.load_parameters
    :members:
    :undoc-members:
