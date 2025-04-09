Installation
===========

Requirements
--------------

The Email Deliverability Library requires:

* Python 3.7 or higher
* Internet connection for some features (blacklist checks, etc.)
* DNS resolution capabilities

Basic Installation
-------------------

You can install the Email Deliverability Library using pip:

.. code-block:: bash

   pip install email_deliverability

Development Installation
----------------------------

If you want to contribute to the library or modify it for your own purposes, you can install it in development mode:

.. code-block:: bash

   git clone https://github.com/innerkore/email-deliverability.git
   cd email-deliverability
   pip install -e .

Dependencies
-------------

The library automatically installs the following dependencies:

* ``dnspython``: For DNS lookups and validation
* ``requests``: For API calls and HTTP requests
* ``cryptography``: For DKIM key generation and signing
* ``schedule``: For periodic resource updates

Verifying Installation
--------------------------

To verify that the installation was successful, you can run:

.. code-block:: python

   import email_deliverability
   print(email_deliverability.__version__)

Next Steps
---------

Once installed, proceed to the :doc:`quickstart` guide to learn how to use the library.