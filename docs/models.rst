Data Models
===========

The Rossum API SDK provides type-safe dataclass models for all API resources.
These models are automatically populated from API responses and provide
clear type hints for all fields.

.. contents:: Table of Contents
   :local:
   :depth: 1

Overview
--------

All models are Python dataclasses with full type annotations. They represent
the structure of data returned by the Rossum API and can also be used when
sending data to the API.

**Key features:**

* Type-safe with full type hints
* Automatic deserialization from API responses
* Possibility to use a custom deserializer
* Support for nested objects
* Optional fields with sensible defaults
* Direct mapping to API documentation


Models
------

.. raw:: html

   <h4>Annotation</h4>

.. autoclass:: rossum_api.models.annotation.Annotation
   :no-index-entry:

.. raw:: html

   <h4>AutomationBlocker</h4>

.. autoclass:: rossum_api.models.automation_blocker.AutomationBlocker
   :no-index-entry:

.. raw:: html

   <h4>AutomationBlockerContent</h4>

.. autoclass:: rossum_api.models.automation_blocker.AutomationBlockerContent
   :no-index-entry:

.. raw:: html

   <h4>Connector</h4>

.. autoclass:: rossum_api.models.connector.Connector
   :no-index-entry:

.. raw:: html

   <h4>Document</h4>

.. autoclass:: rossum_api.models.document.Document
   :no-index-entry:

.. raw:: html

   <h4>DocumentRelation</h4>

.. autoclass:: rossum_api.models.document_relation.DocumentRelation
   :no-index-entry:

.. autoclass:: rossum_api.models.email.Email
   :show-inheritance:

.. raw:: html

   <h4>EmailTemplate</h4>

.. autoclass:: rossum_api.models.email_template.EmailTemplate
   :no-index-entry:

.. raw:: html

   <h4>Hook</h4>

.. autoclass:: rossum_api.models.hook.Hook
   :no-index-entry:

.. raw:: html

   <h4>Inbox</h4>

.. autoclass:: rossum_api.models.inbox.Inbox
   :no-index-entry:

.. raw:: html

   <h4>Organization</h4>

.. autoclass:: rossum_api.models.organization.Organization
   :no-index-entry:

.. raw:: html

   <h4>Queue</h4>

.. autoclass:: rossum_api.models.queue.Queue
   :no-index-entry:

.. raw:: html

   <h4>Rule</h4>

.. autoclass:: rossum_api.models.rule.Rule
   :no-index-entry:

.. raw:: html

   <h4>RuleAction</h4>

.. autoclass:: rossum_api.models.rule.RuleAction
   :no-index-entry:

.. raw:: html

   <h4>Schema</h4>

.. autoclass:: rossum_api.models.schema.Schema
   :no-index-entry:

.. raw:: html

   <h4>Task</h4>

.. autoclass:: rossum_api.models.task.Task
   :no-index-entry:

.. raw:: html

   <h4>Upload</h4>

.. autoclass:: rossum_api.models.upload.Upload
   :no-index-entry:

.. raw:: html

   <h4>User</h4>

.. autoclass:: rossum_api.models.user.User
   :no-index-entry:

.. raw:: html

   <h4>Workspace</h4>

.. autoclass:: rossum_api.models.workspace.Workspace
   :no-index-entry:

Model Usage Examples
--------------------

Creating Model Instances
~~~~~~~~~~~~~~~~~~~~~~~~

Models can be created manually or are automatically deserialized from API responses:

.. code-block:: python

   from rossum_api.models.workspace import Workspace

   # Automatically deserialized from API
   workspace = await client.retrieve_workspace(123)
   print(workspace.name, workspace.id)

   # Manual creation (for testing)
   workspace = Workspace(
       id=123,
       name="My Workspace",
       url="https://elis.rossum.ai/api/v1/workspaces/123",
       organization="https://elis.rossum.ai/api/v1/organizations/1",
       autopilot=False,
   )

Accessing Nested Objects
~~~~~~~~~~~~~~~~~~~~~~~~~

Some models contain references to other models:

.. code-block:: python

   # Annotation can have a nested Document object
   annotation = await client.retrieve_annotation(456)

   # If document is expanded in the API response
   if isinstance(annotation.document, Document):
       print(f"Document: {annotation.document.original_file_name}")
   # Otherwise it's just a URL string
   else:
       print(f"Document URL: {annotation.document}")

Working with Enums
~~~~~~~~~~~~~~~~~~

Models use Python enums for fields with fixed values:

.. code-block:: python

   from rossum_api.models.document_relation import DocumentRelationType

   # Check relation type
   if relation.type == DocumentRelationType.EXPORT:
       print("This is an export relation")

Type Hints
~~~~~~~~~~

All models have full type hints for IDE autocomplete and type checking:

.. code-block:: python

   def process_annotation(annotation: Annotation) -> None:
       # IDE will provide autocomplete for annotation fields
       print(annotation.status)
       print(annotation.content)

       # Type checker will catch errors
       # annotation.nonexistent_field  # Error: Annotation has no attribute 'nonexistent_field'

See Also
--------

* :doc:`clients` - API clients that return these models
* `Rossum API Documentation <https://elis.rossum.ai/api/docs>`_ - Detailed field descriptions
