API Clients
===========

The Rossum API SDK provides both synchronous and asynchronous clients for interacting
with the Rossum API. Both clients offer identical functionality, so choose the one
that best fits your application architecture.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

The external clients are the primary interfaces for interacting with Rossum API.
They handle authentication, pagination, error handling, and provide convenient
methods for all API operations.

**When to use async vs sync:**

* Use :class:`~rossum_api.clients.external_async_client.AsyncRossumAPIClient` when:

  - Your application is already async-based
  - You need to make concurrent API calls
  - You want optimal performance for I/O-bound operations

* Use :class:`~rossum_api.clients.external_sync_client.SyncRossumAPIClient` when:

  - You're working in a traditional synchronous application
  - You're scripting or prototyping

Asynchronous Client
-------------------

.. autoclass:: rossum_api.clients.external_async_client.AsyncRossumAPIClient
   :members:
   :undoc-members:
   :exclude-members: change_user_password, reset_user_password, retrieve_engine, list_engines, retrieve_engine_fields, retrieve_engine_queues

Synchronous Client
------------------

.. autoclass:: rossum_api.clients.external_sync_client.SyncRossumAPIClient
   :members:
   :undoc-members:
   :exclude-members: change_user_password, reset_user_password, retrieve_engine, list_engines, retrieve_engine_fields, retrieve_engine_queues

Client Usage Examples
---------------------

Authentication
~~~~~~~~~~~~~~

Both clients support authentication via username/password credentials or token-based authentication:

.. code-block:: python

   from rossum_api import SyncRossumAPIClient
   from rossum_api.dtos import UserCredentials, Token

   # Username/password authentication
   credentials = UserCredentials(
       username="your.email@example.com",
       password="your-password"
   )

   # Token-based authentication
   credentials = Token(token="your-api-token")

   # Initialize the Rossum API client
   client = SyncRossumAPIClient(base_url="...", credentials=credentials)

Working with Annotations
~~~~~~~~~~~~~~~~~~~~~~~~

**Async version:**

.. code-block:: python

   # Retrieve a single annotation
   annotation = await client.retrieve_annotation(12345)

   # List annotations with filtering
   async for annotation in client.list_annotations(
       status="to_review",
       ordering=["-created_at"]
   ):
       print(annotation.id, annotation.status)

   # Search for annotations
   async for annotation in client.search_for_annotations(
       query={"status": "to_review"},
       ordering=["-created_at"]
   ):
       print(annotation.id, annotation.status)

   # Update annotation
   updated = await client.update_annotation(
       annotation_id=12345,
       data={"status": "confirmed"}
   )

   # Poll annotation until imported
   annotation = await client.poll_annotation_until_imported(12345)

   # Confirm annotation
   await client.confirm_annotation(12345)

**Sync version:**

.. code-block:: python

   # Retrieve a single annotation
   annotation = client.retrieve_annotation(12345)

   # List annotations with filtering
   for annotation in client.list_annotations(
       status="to_review",
       ordering=["-created_at"]
   ):
       print(annotation.id, annotation.status)

   # Search for annotations
   for annotation in client.search_for_annotations(
       query={"status": "to_review"},
       ordering=["-created_at"]
   ):
       print(annotation.id, annotation.status)

   # Update annotation
   updated = client.update_annotation(
       annotation_id=12345,
       data={"status": "confirmed"}
   )

   # Poll annotation until imported
   annotation = client.poll_annotation_until_imported(12345)

   # Confirm annotation
   client.confirm_annotation(12345)

Working with Documents
~~~~~~~~~~~~~~~~~~~~~~

**Async version:**

.. code-block:: python

   # Upload documents (creates tasks)
   tasks = await client.upload_document(
       queue_id=123,
       files=[("path/to/invoice.pdf", "invoice.pdf")]
   )

   # Poll task until completion
   task = await client.poll_task_until_succeeded(tasks[0].id)

   # Retrieve document
   document = await client.retrieve_document(12345)

   # Get document content
   content = await client.retrieve_document_content(12345)

   # Create new document
   document = await client.create_new_document(
       file_name="invoice.pdf",
       file_data=content,
       metadata={"source": "email"}
   )

   # Upload and wait for import in one call
   annotation = await client.upload_and_wait_until_imported(
       queue_id=123,
       filepath="invoice.pdf",
       filename="invoice.pdf"
   )

**Sync version:**

.. code-block:: python

   # Upload documents (creates tasks)
   tasks = client.upload_document(
       queue_id=123,
       files=[("path/to/invoice.pdf", "invoice.pdf")]
   )

   # Poll task until completion
   task = client.poll_task_until_succeeded(tasks[0].id)

   # Retrieve document
   document = client.retrieve_document(12345)

   # Get document content
   content = client.retrieve_document_content(12345)

   # Create new document
   document = client.create_new_document(
       file_name="invoice.pdf",
       file_data=content,
       metadata={"source": "email"}
   )

   # Upload and wait for import in one call
   annotation = client.upload_and_wait_until_imported(
       queue_id=123,
       filepath="invoice.pdf",
       filename="invoice.pdf"
   )

Working with Workspaces and Queues
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Async version:**

.. code-block:: python

   # Create workspace
   workspace = await client.create_new_workspace(data={
       "name": "My Workspace",
       "organization": organization_url,
   })

   # Retrieve workspace
   workspace = await client.retrieve_workspace(123)

   # List workspaces
   async for workspace in client.list_workspaces():
       print(workspace.name)

   # Create queue in workspace
   queue = await client.create_new_queue(data={
       "name": "Invoices",
       "workspace": workspace.url,
       "schema": schema_url,
   })

   # Retrieve queue
   queue = await client.retrieve_queue(456)

   # List queues with filtering
   async for queue in client.list_queues(workspace=workspace.id):
       print(queue.name)

   # Delete queue
   await client.delete_queue(456)

**Sync version:**

.. code-block:: python

   # Create workspace
   workspace = client.create_new_workspace(data={
       "name": "My Workspace",
       "organization": organization_url,
   })

   # Retrieve workspace
   workspace = client.retrieve_workspace(123)

   # List workspaces
   for workspace in client.list_workspaces():
       print(workspace.name)

   # Create queue in workspace
   queue = client.create_new_queue(data={
       "name": "Invoices",
       "workspace": workspace.url,
       "schema": schema_url,
   })

   # Retrieve queue
   queue = client.retrieve_queue(456)

   # List queues with filtering
   for queue in client.list_queues(workspace=workspace.id):
       print(queue.name)

   # Delete queue
   client.delete_queue(456)

Pagination
~~~~~~~~~~

The clients handle pagination automatically:

.. code-block:: python

   # All `list_*` methods automatically handle pagination
   # and yield results one by one
   async for user in client.list_users():
       print(user.email)

   # Lists can be filtered and ordered
   async for queue in client.list_queues(
       workspace=123,
       ordering=["-id"]
   ):
       print(queue.name)

Export Operations
~~~~~~~~~~~~~~~~~

Both export formats are supported:

.. code-block:: python

   # Export annotations to JSON (paginated)
   async for annotation in client.export_annotations_to_json(
       queue_id=123,
       status="confirmed"
   ):
       print(annotation.id)

   # Export annotations to file format (CSV, XML, XLSX)
   from rossum_api.domain_logic.annotations import ExportFileFormats

   async for chunk in client.export_annotations_to_file(
       queue_id=123,
       export_format=ExportFileFormats.CSV,
       status="confirmed"
   ):
       # Process file chunk
       pass

Working with Additional Resources
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The clients also provide methods for managing other API resources:

.. code-block:: python

   # Organizations
   async for org in client.list_organizations():
       print(org.name)

   org = await client.retrieve_organization(123)
   my_org = await client.retrieve_my_organization()

   # Schemas
   schema = await client.create_new_schema(data={
       "name": "Invoice Schema",
       "content": schema_definition
   })

   async for schema in client.list_schemas():
       print(schema.name)

   # Users and Roles
   user = await client.create_new_user(data={
       "email": "user@example.com",
       "first_name": "John",
       "last_name": "Doe"
   })

   async for role in client.list_user_roles():
       print(role.name)

   # Hooks and Connectors
   hook = await client.create_new_hook(data={
       "name": "My Hook",
       "target": "https://example.com/webhook"
   })

   connector = await client.create_new_connector(data={
       "name": "My Connector",
       "connector_type": "webhook"
   })

Authentication and Token Management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Get current authentication token
   token = await client.get_token()

   # Force refresh the token
   token = await client.get_token(refresh=True)

   # Manually authenticate (usually not needed)
   await client.authenticate()

Generic Request Methods
~~~~~~~~~~~~~~~~~~~~~~~

For advanced use cases, raw request methods are available in both clients:

**Async version:**

.. code-block:: python

   # Make paginated requests to custom endpoints
   async for item in client.request_paginated(
       "custom/endpoint",
       ordering=["id"]
   ):
       print(item)

   # Make JSON requests
   response = await client.request_json(
       "POST",
       "custom/endpoint",
       json={"data": "value"}
   )

   # Make raw HTTP requests
   response = await client.request(
       "GET",
       "custom/endpoint"
   )

**Sync version:**

.. code-block:: python

   # Make paginated requests to custom endpoints
   for item in client.request_paginated(
       "custom/endpoint",
       ordering=["id"]
   ):
       print(item)

   # Make JSON requests
   response = client.request_json(
       "POST",
       "custom/endpoint",
       json={"data": "value"}
   )

   # Make raw HTTP requests
   response = client.request(
       "GET",
       "custom/endpoint"
   )

Error Handling
~~~~~~~~~~~~~~

.. code-block:: python

   from httpx import HTTPStatusError

   try:
       annotation = await client.retrieve_annotation(99999)
   except HTTPStatusError as e:
       if e.response.status_code == 404:
           print("Annotation not found")
       else:
           print(f"API error: {e}")

Client Configuration
~~~~~~~~~~~~~~~~~~~~

Both clients support various configuration options:

.. code-block:: python

   from rossum_api.dtos import UserCredentials, Token

   # Using username/password
   client = AsyncRossumAPIClient(
       base_url="https://elis.rossum.ai/api/v1",
       credentials=UserCredentials("user@example.com", "password"),
       timeout=30.0,
       n_retries=5,
       retry_backoff_factor=2.0,
       retry_max_jitter=1.0,
       max_in_flight_requests=8  # async only
   )

   # Using token
   client = AsyncRossumAPIClient(
       base_url="https://elis.rossum.ai/api/v1",
       credentials=Token("your-api-token")
   )

See Also
--------

* :doc:`models` - Data models returned by the clients
* `Rossum API Documentation <https://elis.rossum.ai/api/docs>`_ - Official API reference
