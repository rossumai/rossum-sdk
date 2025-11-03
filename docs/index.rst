Welcome to Rossum API SDK Documentation
=========================================

**rossum-api** provides programmatic access to the `Rossum API <https://api.elis.rossum.ai/docs>`_,
enabling seamless integration of the Rossum platform into Python applications.

This package is focused on accessing the HTTP API. For more advanced usage like Schema Transformations
or interactive CLI tools, please refer to the `Rossum package <https://github.com/rossumai/rossum>`_.

.. note::
   If you need both synchronous and asynchronous API clients, this SDK provides both flavors
   to fit your application's needs.

Key Features
------------

* **Minimal dependencies**: Lightweight with minimal external dependencies
* **API-aligned naming**: Method names map closely to the official API documentation
* **Dual API support**: Choose between synchronous and asynchronous clients
* **Authentication**: Built-in authentication handling
* **Retry mechanism**: Built-in retry mechanism handling throttling API errors
* **Pagination handling**: Automatically merges paginated results into one list
* **Rich methods**: Includes methods for frequent API operations
* **Type-safe**: Returns results as Python dataclasses with full type hints

Installation
------------

Install from PyPI:

.. code-block:: bash

   pip install rossum-api

Or install from the GitHub repository:

.. code-block:: bash

   pip install git+https://github.com/rossumai/rossum-sdk#egg=rossum-api

Quick Start
-----------

Asynchronous Example
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import asyncio
   import os

   from rossum_api import AsyncRossumAPIClient
   from rossum_api.dtos import UserCredentials

   async def main():
       client = AsyncRossumAPIClient(
           base_url="https://elis.rossum.ai/api/v1",
           credentials=UserCredentials(
               os.environ["ELIS_USERNAME"],
               os.environ["ELIS_PASSWORD"]
           ),
       )

       # Create workspace
       workspace = await client.create_new_workspace(data={
           "name": "My Workspace",
           "organization": "https://elis.rossum.ai/api/v1/organizations/123",
       })

       # Retrieve workspace
       ws = await client.retrieve_workspace(workspace.id)
       print("Workspace:", ws)

       # List workspaces
       async for w in client.list_workspaces(ordering=["-id"]):
           print(w)

   asyncio.run(main())

Synchronous Example
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import os

   from rossum_api import SyncRossumAPIClient
   from rossum_api.dtos import UserCredentials

   def main():
       client = SyncRossumAPIClient(
           base_url="https://elis.rossum.ai/api/v1",
           credentials=UserCredentials(
               os.environ["ELIS_USERNAME"],
               os.environ["ELIS_PASSWORD"]
           ),
       )

       # Create workspace
       workspace = client.create_new_workspace(data={
           "name": "My Workspace",
           "organization": "https://elis.rossum.ai/api/v1/organizations/123",
       })

       # Retrieve workspace
       ws = client.retrieve_workspace(workspace.id)
       print("Workspace:", ws)

       # List workspaces
       for w in client.list_workspaces(ordering=["-id"]):
           print(w)

   main()

API Reference
-------------

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   clients
   models

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
