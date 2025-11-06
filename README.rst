Rossum API
==========

|pypi| |build| |coverage| |ruff| |docs| |license|

.. |pypi| image:: https://img.shields.io/pypi/v/rossum-api.svg
   :target: https://pypi.org/project/rossum-api/
   :alt: PyPI version

.. |build| image:: https://github.com/rossumai/rossum-sdk/actions/workflows/test-and-deploy.yaml/badge.svg
   :target: https://github.com/rossumai/rossum-sdk/actions
   :alt: Build Status

.. |coverage| image:: https://codecov.io/gh/rossumai/rossum-sdk/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/rossumai/rossum-sdk
   :alt: Coverage

.. |ruff| image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
   :target: https://github.com/astral-sh/ruff
   :alt: Code style: Ruff

.. |docs| image:: https://img.shields.io/badge/docs-read-blue.svg
   :target: https://rossumai.github.io/rossum-api/
   :alt: Documentation

.. |license| image:: https://img.shields.io/pypi/l/rossum.svg
   :alt: MIT licence

**rossum-api** provides Python programmatic access to the `Rossum API <https://api.elis.rossum.ai/docs>`_ and other useful tooling
enabling seamless integration of the Rossum platform into Python applications.

It is a replacement for `Rossum package <https://github.com/rossumai/rossum>`_. In case of any missing functionality,
please open an issue or a pull request.

For comprehensive API reference and detailed examples, visit our `documentation <https://rossumai.github.io/rossum-api/>`_.

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

The easiest way is to install the package from PyPI:

.. code-block:: bash

   pip install rossum-api

or from the github repo:

.. code-block:: bash

   pip install git+https://github.com/rossumai/rossum-sdk#egg=rossum-api

You can eventually download an installation file from `GitHub releases <https://github.com/rossumai/rossum-sdk/releases>`_
and install it manually.

Usage
-----

Python API
~~~~~~~~~~

The **rossum-api** library can be used to communicate with Rossum API, instead of using ``requests`` library directly. The advantages of using **rossum-api**:

* it contains a function that merges the paginated results into a single list so the user does not need to get results page by page and take care of their merging,
* it comes with both synchronous and asynchronous API, so you can choose the approach you need,
* it takes care of authenticating the user,
* it includes many methods for common actions that you don't need to write by yourself from scratch,
* it returns the result as a Python first-class object (dataclass), so you don't need to parse the JSON by yourself,
* it maps method naming as close as possible to `API docs <https://elis.rossum.ai/api/docs>`_,
* in case the API version changes, the change will be implemented in the library by the Rossum team for all users.
* it has minimal dependencies

Examples
~~~~~~~~

You can choose between asynchronous and synchronous clients. Both are exactly the same in terms of features.

Async version
~~~~~~~~~~~~~

.. code-block:: python

   import asyncio
   import os
   from rossum_api import AsyncRossumAPIClient
   from rossum_api.dtos import UserCredentials

   WORKSPACE = {
       "name": "Rossum Client NG Test",
       "organization": "https://elis.rossum.ai/api/v1/organizations/116390",
   }


   async def main_with_async_client() -> None:
       client = AsyncRossumAPIClient(
           base_url="https://elis.rossum.ai/api/v1",
           credentials=UserCredentials(os.environ["ELIS_USERNAME"], os.environ["ELIS_PASSWORD"]),
       )
       ws = await client.create_new_workspace(data=WORKSPACE)
       workspace_id = ws.id
       ws = await client.retrieve_workspace(workspace_id)
       print("GET result:", ws)
       print("LIST results:")
       async for w in client.list_workspaces(ordering=["-id"], name=WORKSPACE["name"]):
           print(w)
       await client.delete_workspace(workspace_id)
       print(f"Workspace {workspace_id} deleted.")


   asyncio.run(main_with_async_client())

Sync version
~~~~~~~~~~~~

.. code-block:: python

   import os

   from rossum_api import SyncRossumAPIClient
   from rossum_api.dtos import UserCredentials

   WORKSPACE = {
       "name": "Rossum Client NG Test",
       "organization": "https://elis.rossum.ai/api/v1/organizations/116390",
   }


   def main_with_sync_client() -> None:
       client = SyncRossumAPIClient(
           base_url="https://elis.rossum.ai/api/v1",
           credentials=UserCredentials(os.environ["ELIS_USERNAME"], os.environ["ELIS_PASSWORD"]),
       )
       ws = client.create_new_workspace(data=WORKSPACE)
       workspace_id = ws.id
       ws = client.retrieve_workspace(workspace_id)
       print("GET result:", ws)
       print("LIST results:")
       for w in client.list_workspaces(ordering=["-id"], name=WORKSPACE["name"]):
           print(w)
       client.delete_workspace(workspace_id)
       print(f"Workspace {workspace_id} deleted.")


   main_with_sync_client()

Local development
-----------------

Pull the repository, create a virtual environment, and install the package from the source with test dependencies:

.. code-block:: bash

   # Create and activate virtual environment
   python -m venv .env
   source .env/bin/activate

   # Install in editable mode with test dependencies
   pip install -e .[tests]

We use ruff for linting and formatting. Run all pre-commit hooks with:

.. code-block:: bash

   pre-commit run --all-files

Or run specific tools:

.. code-block:: bash

   # Linting and formatting
   pre-commit run ruff --all-files
   pre-commit run ruff-format --all-files

   # Type checking
   pre-commit run mypy --all-files

   # Run tests
   pytest

License
-------

MIT
