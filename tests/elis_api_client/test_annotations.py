from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from rossum_api.domain_logic.resources import Resource
from rossum_api.models.annotation import Annotation
from rossum_api.models.automation_blocker import AutomationBlocker, AutomationBlockerContent
from rossum_api.models.document import Document
from rossum_api.models.user import User


@pytest.fixture
def dummy_annotation():
    return {
        "document": "https://elis.rossum.ai/api/v1/documents/314628",
        "id": 314528,
        "queue": "https://elis.rossum.ai/api/v1/queues/8199",
        "schema": "https://elis.rossum.ai/api/v1/schemas/95",
        "relations": [],
        "pages": ["https://elis.rossum.ai/api/v1/pages/558598"],
        "creator": "https://elis.rossum.ai/api/v1/users/1",
        "created_at": "2021-04-26T10:08:03.856648Z",
        "modifier": None,
        "modified_at": None,
        "confirmed_at": None,
        "exported_at": None,
        "assigned_at": None,
        "status": "to_review",
        "rir_poll_id": "54f6b9ecfa751789f71ddf12",
        "messages": None,
        "url": "https://elis.rossum.ai/api/v1/annotations/314528",
        "content": "https://elis.rossum.ai/api/v1/annotations/314528/content",
        "time_spent": 0,
        "metadata": {},
        "related_emails": [],
        "email": "https://elis.rossum.ai/api/v1/emails/96743",
        "automation_blocker": None,
        "email_thread": "https://elis.rossum.ai/api/v1/email_threads/34567",
        "has_email_thread_with_replies": True,
        "has_email_thread_with_new_replies": False,
        "modified_by": None,
        "deleted_at": None,
        "export_failed_at": None,
        "purged_at": None,
        "rejected_at": None,
        "confirmed_by": None,
        "deleted_by": None,
        "exported_by": None,
        "purged_by": None,
        "rejected_by": None,
        "organization": "https://elis.rossum.ai/api/v1/organizations/1",
        "prediction": None,
        "assignees": [],
        "labels": [],
        "training_enabled": True,
        "einvoice": False,
    }


@pytest.fixture
def dummy_annotation_with_sideloads():
    return {
        "document": {
            "id": 3244308,
            "url": "https://elis.develop.r8.lol/api/v1/documents/3244308",
            "s3_name": "7731c4d28b3bf6ae5e29f933798b1393",
            "parent": None,
            "email": None,
            "mime_type": "application/pdf",
            "creator": "https://elis.develop.r8.lol/api/v1/users/71531",
            "created_at": "2022-07-12T08:16:41.731996Z",
            "arrived_at": "2022-07-12T08:16:41.731996Z",
            "original_file_name": "test_lacte1.pdf",
            "content": "https://elis.develop.r8.lol/api/v1/documents/3244308/content",
            "attachment_status": None,
            "metadata": {},
            "annotations": ["https://elis.develop.r8.lol/api/v1/annotations/3232238"],
        },
        "id": 3232238,
        "queue": "https://elis.develop.r8.lol/api/v1/queues/764624",
        "schema": "https://elis.develop.r8.lol/api/v1/schemas/325761",
        "relations": ["https://elis.develop.r8.lol/api/v1/relations/15338"],
        "pages": [
            "https://elis.develop.r8.lol/api/v1/pages/3481780",
            "https://elis.develop.r8.lol/api/v1/pages/3481781",
        ],
        "creator": "https://elis.develop.r8.lol/api/v1/users/71531",
        "modifier": {
            "id": 71531,
            "url": "https://elis.develop.r8.lol/api/v1/users/71531",
            "first_name": "",
            "last_name": "",
            "email": "rir.e2e.tests@rossum.ai",
            "email_verified": True,
            "date_joined": "2021-08-02T14:11:41.692653Z",
            "username": "rir.e2e.tests@rossum.ai",
            "groups": ["https://elis.develop.r8.lol/api/v1/groups/3"],
            "organization": "https://elis.develop.r8.lol/api/v1/organizations/40507",
            "queues": [],
            "is_active": True,
            "last_login": "2022-07-13T08:41:35.934997Z",
            "ui_settings": {},
            "metadata": {},
            "oidc_id": None,
            "auth_type": "password",
        },
        "created_at": "2022-07-12T08:16:41.910102Z",
        "modified_at": "2022-07-12T08:17:18.961411Z",
        "confirmed_at": None,
        "exported_at": "2022-07-12T08:17:19.957129Z",
        "assigned_at": "2022-07-12T08:17:18.082554Z",
        "status": "exported",
        "rir_poll_id": "ed764b2144fa43118bdb11a9",
        "messages": [],
        "url": "https://elis.develop.r8.lol/api/v1/annotations/3232238",
        "content": [],
        "time_spent": 0.0,
        "metadata": {},
        "automated": False,
        "suggested_edit": None,
        "related_emails": [],
        "email": None,
        "automation_blocker": {
            "id": 981916,
            "url": "https://elis.develop.r8.lol/api/v1/automation_blockers/981916",
            "content": [
                {"type": "automation_disabled", "level": "annotation"},
                {
                    "level": "datapoint",
                    "type": "error_message",
                    "samples": [
                        {"details": {"message_content": ["Total Amount is most likely not empty"]}}
                    ],
                },
            ],
            "annotation": "https://elis.develop.r8.lol/api/v1/annotations/3232238",
        },
        "email_thread": None,
        "has_email_thread_with_replies": False,
        "has_email_thread_with_new_replies": False,
        "organization": "https://elis.develop.r8.lol/api/v1/organizations/40507",
    }


@pytest.mark.asyncio
class TestAnnotations:
    async def test_list_annotations(self, elis_client, dummy_annotation, mock_generator):
        client, http_client = elis_client
        http_client.fetch_all.return_value = mock_generator(dummy_annotation)

        annotations = client.list_annotations()

        async for a in annotations:
            assert a == Annotation(**dummy_annotation)

        http_client.fetch_all.assert_called_with(Resource.Annotation, (), (), ())

    async def test_list_annotations_with_sideloads(
        self, elis_client, dummy_annotation_with_sideloads, mock_generator
    ):
        client, http_client = elis_client
        http_client.fetch_all.return_value = mock_generator(dummy_annotation_with_sideloads)

        annotations = client.list_annotations(
            sideloads=["documents", "automation_blockers", "content", "modifiers"],
            content_schema_ids=["325164"],
        )

        async for a in annotations:
            annotation = Annotation(**dummy_annotation_with_sideloads)
            modifier = User(**annotation.modifier)
            annotation.modifier = modifier
            automation_blocker = Document(**annotation.document)
            annotation.document = automation_blocker
            automation_blocker = AutomationBlocker(**annotation.automation_blocker)
            automation_blocker.content = [
                AutomationBlockerContent(**content) for content in automation_blocker.content
            ]
            annotation.automation_blocker = automation_blocker
            annotation.content = [
                AutomationBlockerContent(**content) for content in annotation.content
            ]
            assert a == annotation

        http_client.fetch_all.assert_called_with(
            Resource.Annotation,
            (),
            ["documents", "automation_blockers", "content", "modifiers"],
            ["325164"],
        )

    async def test_list_annotations_with_content_sideloads_without_schema_ids(self, elis_client):
        client, http_client = elis_client
        http_client.fetch_all = MagicMock()

        with pytest.raises(ValueError):
            async for _ in client.list_annotations(
                sideloads=["content"],
            ):
                pass

        assert not http_client.fetch_all.called

    async def test_search_for_annotations(self, elis_client, dummy_annotation, mock_generator):
        client, http_client = elis_client
        http_client.fetch_all.return_value = mock_generator(dummy_annotation)

        annotations = client.search_for_annotations({"$and": []}, {"string": "expl"})

        async for a in annotations:
            assert a == Annotation(**dummy_annotation)

        http_client.fetch_all_by_url.assert_called_with(
            "annotations/search",
            (),
            (),
            json={"query": {"$and": []}, "query_string": {"string": "expl"}},
            method="POST",
        )

    async def test_retrieve_annotation(self, elis_client, dummy_annotation):
        client, http_client = elis_client
        http_client.fetch_one.return_value = dummy_annotation

        aid = dummy_annotation["id"]
        annotation = await client.retrieve_annotation(aid)

        assert annotation == Annotation(**dummy_annotation)

        http_client.fetch_one.assert_called_with(Resource.Annotation, aid)

    async def test_retrieve_annotation_with_sideloads(self, elis_client, dummy_annotation):
        client, http_client = elis_client
        # Copy the annotation to prevent changing dummy_annotation by side effects
        http_client.fetch_one.return_value = dummy_annotation.copy()
        http_client.request_json.return_value = {"content": []}

        aid = dummy_annotation["id"]
        annotation = await client.retrieve_annotation(aid, sideloads=["content"])

        assert annotation == Annotation(**{**dummy_annotation, "content": []})

        http_client.fetch_one.assert_called_with(Resource.Annotation, aid)

    async def test_poll_annotation(self, elis_client, dummy_annotation):
        def is_imported(annotation):
            return annotation.status not in ("importing", "created")

        client, http_client = elis_client
        in_progress_annotation = {**dummy_annotation, "status": "importing"}
        # First, return annotation in importing, than to_review state
        # Copy the annotation to prevent changing dummy_annotation by side effects
        http_client.fetch_one.side_effect = [in_progress_annotation, dummy_annotation.copy()]
        # Return sideloaded content
        http_client.request_json.return_value = {"content": []}

        with patch("asyncio.sleep") as sleep_mock:
            annotation = await client.poll_annotation(
                dummy_annotation["id"], is_imported, sleep_s=2, sideloads=["content"]
            )

        assert annotation == Annotation(**{**dummy_annotation, "content": []})

        sleep_mock.assert_called_once_with(2)

    async def test_poll_annotation_until_imported(self, elis_client, dummy_annotation):
        client, http_client = elis_client
        in_progress_annotation = {**dummy_annotation, "status": "importing"}
        # First, return annotation in importing, than to_review state
        # Copy the annotation to prevent changing dummy_annotation by side effects
        http_client.fetch_one.side_effect = [in_progress_annotation, dummy_annotation.copy()]
        # Return sideloaded content
        http_client.request_json.return_value = {"content": []}

        with patch("asyncio.sleep") as sleep_mock:
            annotation = await client.poll_annotation_until_imported(
                dummy_annotation["id"], sleep_s=2, sideloads=["content"]
            )

        assert annotation == Annotation(**{**dummy_annotation, "content": []})
        sleep_mock.assert_called_once_with(2)

    async def test_upload_and_wait_until_imported(self, elis_client, dummy_annotation):
        client, http_client = elis_client
        in_progress_annotation = {**dummy_annotation, "status": "importing"}
        # Mock uploading a document
        http_client.upload.side_effect = [
            {"results": [{"annotation": f"/annotation/{dummy_annotation['id']}"}]}
        ]
        # First, return annotation in importing, than to_review state
        # Copy the annotation to prevent changing dummy_annotation by side effects
        http_client.fetch_one.side_effect = [in_progress_annotation, dummy_annotation.copy()]
        # Return sideloaded content
        http_client.request_json.return_value = {"content": []}

        with patch("asyncio.sleep") as sleep_mock:
            annotation = await client.upload_and_wait_until_imported(
                queue_id=8199,
                filepath="tests/data/sample_invoice.pdf",
                filename="document.pdf",
                sleep_s=2,
                sideloads=["content"],
            )

        assert annotation == Annotation(**{**dummy_annotation, "content": []})

        sleep_mock.assert_called_once_with(2)

    async def test_start_annotation(self, elis_client, dummy_annotation):
        client, http_client = elis_client
        http_client.replace.return_value = dummy_annotation

        aid = dummy_annotation["id"]

        await client.start_annotation(aid)
        http_client.request_json.assert_called_with("POST", f"annotations/{aid}/start")

    async def test_update_annotation(self, elis_client, dummy_annotation):
        client, http_client = elis_client
        http_client.replace.return_value = dummy_annotation

        aid = dummy_annotation["id"]
        data = {
            "document": "https://elis.rossum.ai/api/v1/documents/315877",
            "queue": "https://elis.rossum.ai/api/v1/queues/8236",
            "status": "postponed",
        }
        annotation = await client.update_annotation(aid, data)

        assert annotation == Annotation(**dummy_annotation)

        http_client.replace.assert_called_with(Resource.Annotation, aid, data)

    async def test_update_part_annotation(self, elis_client, dummy_annotation):
        client, http_client = elis_client
        http_client.update.return_value = dummy_annotation

        aid = dummy_annotation["id"]
        data = {
            "status": "deleted",
        }
        annotation = await client.update_part_annotation(aid, data)

        assert annotation == Annotation(**dummy_annotation)

        http_client.update.assert_called_with(Resource.Annotation, aid, data)

    async def test_bulk_update_annotation_data(self, elis_client, dummy_annotation):
        client, http_client = elis_client
        http_client.request_json.return_value = dummy_annotation

        aid = dummy_annotation["id"]
        operations = [{"id": 2510559656, "op": "remove"}, {"id": 2510559657, "op": "remove"}]
        await client.bulk_update_annotation_data(aid, operations)

        http_client.request_json.assert_called_with(
            "POST", f"annotations/{aid}/content/operations", json={"operations": operations}
        )

    async def test_confirm_annotation(self, elis_client, dummy_annotation):
        client, http_client = elis_client
        http_client.replace.return_value = dummy_annotation

        aid = dummy_annotation["id"]

        await client.confirm_annotation(aid)
        http_client.request_json.assert_called_with("POST", f"annotations/{aid}/confirm")

    async def test_create_new_annotation(self, elis_client, dummy_annotation):
        client, http_client = elis_client
        http_client.create.return_value = dummy_annotation

        data = {
            "status": "created",
            "document": dummy_annotation["document"],
            "queue": dummy_annotation["queue"],
        }
        annotation = await client.create_new_annotation(data)

        assert annotation == Annotation(**dummy_annotation)

        http_client.create.assert_called_with(Resource.Annotation, data)

    async def test_delete_annotation(self, elis_client, dummy_annotation):
        client, http_client = elis_client

        aid = dummy_annotation["id"]
        await client.delete_annotation(aid)

        http_client.request.assert_called_with(
            "POST", url=f"{Resource.Annotation.value}/{aid}/delete"
        )

    async def test_cancel_annotation(self, elis_client, dummy_annotation):
        client, http_client = elis_client

        aid = dummy_annotation["id"]
        await client.cancel_annotation(aid)

        http_client.request.assert_called_with(
            "POST", url=f"{Resource.Annotation.value}/{aid}/cancel"
        )


class TestAnnotationsSync:
    def test_list_annotations(self, elis_client_sync, dummy_annotation):
        client, http_client = elis_client_sync
        http_client.fetch_resources.return_value = iter((dummy_annotation,))

        annotations = client.list_annotations()

        for a in annotations:
            assert a == Annotation(**dummy_annotation)

        http_client.fetch_resources.assert_called_with(Resource.Annotation, (), (), ())

    def test_list_annotations_with_sideloads(
        self, elis_client_sync, dummy_annotation_with_sideloads
    ):
        client, http_client = elis_client_sync
        http_client.fetch_resources.return_value = iter((dummy_annotation_with_sideloads,))

        annotations = client.list_annotations(
            sideloads=["documents", "automation_blockers", "content", "modifiers"],
            content_schema_ids=["325164"],
        )

        for a in annotations:
            annotation = Annotation(**dummy_annotation_with_sideloads)
            modifier = User(**annotation.modifier)
            annotation.modifier = modifier
            automation_blocker = Document(**annotation.document)
            annotation.document = automation_blocker
            automation_blocker = AutomationBlocker(**annotation.automation_blocker)
            automation_blocker.content = [
                AutomationBlockerContent(**content) for content in automation_blocker.content
            ]
            annotation.automation_blocker = automation_blocker
            annotation.content = [
                AutomationBlockerContent(**content) for content in annotation.content
            ]
            assert a == annotation

        http_client.fetch_resources.assert_called_with(
            Resource.Annotation,
            (),
            ["documents", "automation_blockers", "content", "modifiers"],
            ["325164"],
        )

    def test_list_annotations_with_content_sideloads_without_schema_ids(self, elis_client_sync):
        client, http_client = elis_client_sync
        http_client.fetch_all = MagicMock()

        with pytest.raises(ValueError):
            for _ in client.list_annotations(
                sideloads=["content"],
            ):
                pass

        assert not http_client.fetch_all.called

    def test_search_for_annotations(self, elis_client_sync, dummy_annotation):
        client, http_client = elis_client_sync
        http_client.fetch_resources.return_value = iter((dummy_annotation,))

        annotations = client.search_for_annotations({"$and": []}, {"string": "expl"})

        for a in annotations:
            assert a == Annotation(**dummy_annotation)

        http_client.fetch_resources_by_url.assert_called_with(
            "annotations/search",
            (),
            (),
            json={"query": {"$and": []}, "query_string": {"string": "expl"}},
            method="POST",
        )

    def test_retrieve_annotation(self, elis_client_sync, dummy_annotation):
        client, http_client = elis_client_sync
        http_client.fetch_resource.return_value = dummy_annotation

        aid = dummy_annotation["id"]
        annotation = client.retrieve_annotation(aid)

        assert annotation == Annotation(**dummy_annotation)

        http_client.fetch_resource.assert_called_with(Resource.Annotation, aid)

    def test_poll_annotation(self, elis_client_sync, dummy_annotation):
        def is_imported(annotation):
            return annotation.status not in ("importing", "created")

        client, http_client = elis_client_sync
        in_progress_annotation = {**dummy_annotation, "status": "importing"}
        # First, return annotation in importing, than to_review state
        # Copy the annotation to prevent changing dummy_annotation by side effects
        http_client.fetch_resource.side_effect = [
            in_progress_annotation,
            dummy_annotation.copy(),
            [],
        ]

        with patch("time.sleep") as sleep_mock:
            annotation = client.poll_annotation(dummy_annotation["id"], is_imported, sleep_s=2)

        assert annotation == Annotation(**dummy_annotation)

        sleep_mock.assert_called_once_with(2)

    def test_poll_annotation_until_imported(self, elis_client_sync, dummy_annotation):
        client, http_client = elis_client_sync
        in_progress_annotation = {**dummy_annotation, "status": "importing"}
        # First, return annotation in importing, than to_review state
        # Copy the annotation to prevent changing dummy_annotation by side effects
        http_client.fetch_resource.side_effect = [
            in_progress_annotation,
            dummy_annotation.copy(),
            [],
        ]
        # Return sideloaded content
        http_client.request_json.return_value = {"content": []}

        with patch("time.sleep") as sleep_mock:
            annotation = client.poll_annotation_until_imported(dummy_annotation["id"], sleep_s=2)

        assert annotation == Annotation(**dummy_annotation)

        sleep_mock.assert_called_once_with(2)

    def test_upload_and_wait_until_imported(self, elis_client_sync, dummy_annotation):
        client, http_client = elis_client_sync
        in_progress_annotation = {**dummy_annotation, "status": "importing"}
        # Mock uploading a document
        http_client.upload.side_effect = [
            {"results": [{"annotation": f"/annotation/{dummy_annotation['id']}"}]}
        ]
        # First, return annotation in importing, than to_review state
        # Copy the annotation to prevent changing dummy_annotation by side effects
        http_client.fetch_resource.side_effect = [in_progress_annotation, dummy_annotation.copy()]
        # Return sideloaded content
        http_client.request_json.return_value = {"content": []}

        with patch("time.sleep") as sleep_mock:
            annotation = client.upload_and_wait_until_imported(
                queue_id=8199,
                filepath="tests/data/sample_invoice.pdf",
                filename="document.pdf",
                sleep_s=2,
            )

        assert annotation == Annotation(**dummy_annotation)

        sleep_mock.assert_called_once_with(2)

    def test_start_annotation(self, elis_client_sync, dummy_annotation):
        client, http_client = elis_client_sync
        http_client.replace.return_value = dummy_annotation

        aid = dummy_annotation["id"]

        client.start_annotation(aid)
        http_client.request_json.assert_called_with("POST", f"annotations/{aid}/start")

    def test_update_annotation(self, elis_client_sync, dummy_annotation):
        client, http_client = elis_client_sync
        http_client.replace.return_value = dummy_annotation

        aid = dummy_annotation["id"]
        data = {
            "document": "https://elis.rossum.ai/api/v1/documents/315877",
            "queue": "https://elis.rossum.ai/api/v1/queues/8236",
            "status": "postponed",
        }
        annotation = client.update_annotation(aid, data)

        assert annotation == Annotation(**dummy_annotation)

        http_client.replace.assert_called_with(Resource.Annotation, aid, data)

    def test_update_part_annotation(self, elis_client_sync, dummy_annotation):
        client, http_client = elis_client_sync
        http_client.update.return_value = dummy_annotation

        aid = dummy_annotation["id"]
        data = {
            "status": "deleted",
        }
        annotation = client.update_part_annotation(aid, data)

        assert annotation == Annotation(**dummy_annotation)

        http_client.update.assert_called_with(Resource.Annotation, aid, data)

    def test_bulk_update_annotation_data(self, elis_client_sync, dummy_annotation):
        client, http_client = elis_client_sync
        http_client.request_json.return_value = dummy_annotation

        aid = dummy_annotation["id"]
        operations = [{"id": 2510559656, "op": "remove"}, {"id": 2510559657, "op": "remove"}]
        client.bulk_update_annotation_data(aid, operations)

        http_client.request_json.assert_called_with(
            "POST", f"annotations/{aid}/content/operations", json={"operations": operations}
        )

    def test_confirm_annotation(self, elis_client_sync, dummy_annotation):
        client, http_client = elis_client_sync
        http_client.replace.return_value = dummy_annotation

        aid = dummy_annotation["id"]

        client.confirm_annotation(aid)
        http_client.request_json.assert_called_with("POST", f"annotations/{aid}/confirm")

    def test_create_new_annotation(self, elis_client_sync, dummy_annotation):
        client, http_client = elis_client_sync
        http_client.create.return_value = dummy_annotation

        data = {
            "status": "created",
            "document": dummy_annotation["document"],
            "queue": dummy_annotation["queue"],
        }
        annotation = client.create_new_annotation(data)

        assert annotation == Annotation(**dummy_annotation)

        http_client.create.assert_called_with(Resource.Annotation, data)

    def test_delete_annotation(self, elis_client_sync, dummy_annotation):
        client, http_client = elis_client_sync

        aid = dummy_annotation["id"]
        client.delete_annotation(aid)

        http_client.request.assert_called_with(
            "POST", url=f"{Resource.Annotation.value}/{aid}/delete"
        )

    def test_cancel_annotation(self, elis_client_sync, dummy_annotation):
        client, http_client = elis_client_sync

        aid = dummy_annotation["id"]
        client.cancel_annotation(aid)

        http_client.request.assert_called_with(
            "POST", url=f"{Resource.Annotation.value}/{aid}/cancel"
        )
