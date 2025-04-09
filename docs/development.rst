Development Guide
===============

This guide provides information for developers who want to contribute to the Email Deliverability Library.

Setting Up the Development Environment
---------------------------------------------

1. Clone the repository:

   .. code-block:: bash
   
       git clone https://github.com/innerkore/email-deliverability.git
       cd email-deliverability

2. Create a virtual environment and install development dependencies:

   .. code-block:: bash
   
       python -m venv venv
       source venv/bin/activate  # On Windows: venv\Scripts\activate
       pip install -e ".[dev]"

Running Tests
--------------

The library uses unittest for testing. To run all tests:

.. code-block:: bash

    python -m unittest discover tests

For more detailed test output:

.. code-block:: bash

    python -m unittest discover -v tests

Code Style
---------

We follow PEP 8 guidelines for Python code. Some key points:

- Use 4 spaces for indentation
- Maximum line length of 100 characters
- Use descriptive variable and function names
- Include docstrings for all classes and functions

Building Documentation
--------------------------

The documentation is built using Sphinx. To build the documentation:

.. code-block:: bash

    cd docs
    make html

The built documentation will be available in the `docs/_build/html` directory.

Contributing
-------------

1. Create a new branch for your feature or bugfix:

   .. code-block:: bash
   
       git checkout -b feature/your-feature-name

2. Make your changes and ensure all tests pass:

   .. code-block:: bash
   
       python -m unittest discover tests

3. Update documentation if necessary

4. Submit a pull request with a clear description of your changes

Releasing New Versions
----------------------

1. Update version number in:
   - `email_deliverability/__init__.py`
   - `setup.py`
   - `docs/conf.py`

2. Update the changelog with the new version and changes

3. Create a tag for the new version:

   .. code-block:: bash
   
       git tag v0.1.0
       git push --tags

4. Build and publish to PyPI:

   .. code-block:: bash
   
       ./scripts/publish.sh