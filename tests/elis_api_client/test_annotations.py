from __future__ import annotations

import pytest
from mock.mock import MagicMock, patch

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
            "content": [{"type": "automation_disabled", "level": "annotation"}],
            "annotation": "https://elis.develop.r8.lol/api/v1/annotations/3232238",
        },
        "email_thread": None,
        "has_email_thread_with_replies": False,
        "has_email_thread_with_new_replies": False,
        "organization": "https://elis.develop.r8.lol/api/v1/organizations/40507",
    }


@pytest.mark.asyncio
class TestAnnotations:
    async def test_list_all_annotations(self, elis_client, dummy_annotation, mock_generator):
        client, http_client = elis_client
        http_client.fetch_all.return_value = mock_generator(dummy_annotation)

        annotations = client.list_all_annotations()

        async for a in annotations:
            assert a == Annotation(**dummy_annotation)

        http_client.fetch_all.assert_called_with("annotations", (), (), ())

    async def test_list_all_annotations_with_sideloads(
        self, elis_client, dummy_annotation_with_sideloads, mock_generator
    ):
        client, http_client = elis_client
        http_client.fetch_all.return_value = mock_generator(dummy_annotation_with_sideloads)

        annotations = client.list_all_annotations(
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
            "annotations",
            (),
            ["documents", "automation_blockers", "content", "modifiers"],
            ["325164"],
        )

    async def test_list_all_annotations_with_content_sideloads_without_schema_ids(
        self, elis_client
    ):
        client, http_client = elis_client
        http_client.fetch_all = MagicMock()

        with pytest.raises(ValueError):
            async for _ in client.list_all_annotations(
                sideloads=["content"],
            ):
                pass

        assert not http_client.fetch_all.called

    async def test_retrieve_annotation(self, elis_client, dummy_annotation):
        client, http_client = elis_client
        http_client.fetch_one.return_value = dummy_annotation

        aid = dummy_annotation["id"]
        annotation = await client.retrieve_annotation(aid)

        assert annotation == Annotation(**dummy_annotation)

        http_client.fetch_one.assert_called_with("annotations", aid)

    async def test_retrieve_annotation_with_sideloads(self, elis_client, dummy_annotation):
        client, http_client = elis_client
        http_client.fetch_one.return_value = dummy_annotation
        http_client.request_json.return_value = {"content": []}

        aid = dummy_annotation["id"]
        annotation = await client.retrieve_annotation(aid, sideloads=["content"])

        assert annotation == Annotation(**{**dummy_annotation, "content": []})

        http_client.fetch_one.assert_called_with("annotations", aid)

    async def test_poll_annotation(self, elis_client, dummy_annotation):
        def is_imported(annotation):
            return annotation.status != "importing"

        client, http_client = elis_client
        in_progress_annotation = {**dummy_annotation, "status": "importing"}
        # First, return annotation in importing, than to_review state
        http_client.fetch_one.side_effect = [in_progress_annotation, dummy_annotation]
        # Return sideloaded content
        http_client.request_json.return_value = {"content": []}

        with patch("asyncio.sleep") as sleep_mock:
            annotation = await client.poll_annotation(
                dummy_annotation["id"], is_imported, sleep_s=2, sideloads=["content"]
            )

        assert annotation == Annotation(**dummy_annotation)

        sleep_mock.assert_called_once_with(2)

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

        http_client.replace.assert_called_with("annotations", aid, data)

    async def test_update_part_annotation(self, elis_client, dummy_annotation):
        client, http_client = elis_client
        http_client.update.return_value = dummy_annotation

        aid = dummy_annotation["id"]
        data = {
            "status": "deleted",
        }
        annotation = await client.update_part_annotation(aid, data)

        assert annotation == Annotation(**dummy_annotation)

        http_client.update.assert_called_with("annotations", aid, data)


class TestAnnotationsSync:
    def test_list_all_annotations(self, elis_client_sync, dummy_annotation, mock_generator):
        client, http_client = elis_client_sync
        http_client.fetch_all.return_value = mock_generator(dummy_annotation)

        annotations = client.list_all_annotations()

        for a in annotations:
            assert a == Annotation(**dummy_annotation)

        http_client.fetch_all.assert_called_with("annotations", (), (), ())

    def test_list_all_annotations_with_sideloads(
        self, elis_client_sync, dummy_annotation_with_sideloads, mock_generator
    ):
        client, http_client = elis_client_sync
        http_client.fetch_all.return_value = mock_generator(dummy_annotation_with_sideloads)

        annotations = client.list_all_annotations(
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

        http_client.fetch_all.assert_called_with(
            "annotations",
            (),
            ["documents", "automation_blockers", "content", "modifiers"],
            ["325164"],
        )

    def test_list_all_annotations_with_content_sideloads_without_schema_ids(
        self, elis_client_sync
    ):
        client, http_client = elis_client_sync
        http_client.fetch_all = MagicMock()

        with pytest.raises(ValueError):
            for _ in client.list_all_annotations(
                sideloads=["content"],
            ):
                pass

        assert not http_client.fetch_all.called

    def test_retrieve_annotation(self, elis_client_sync, dummy_annotation):
        client, http_client = elis_client_sync
        http_client.fetch_one.return_value = dummy_annotation

        aid = dummy_annotation["id"]
        annotation = client.retrieve_annotation(aid)

        assert annotation == Annotation(**dummy_annotation)

        http_client.fetch_one.assert_called_with("annotations", aid)

    def test_retrieve_annotation_with_sideloads(self, elis_client_sync, dummy_annotation):
        client, http_client = elis_client_sync
        http_client.fetch_one.return_value = dummy_annotation
        http_client.request_json.return_value = {"content": []}

        aid = dummy_annotation["id"]
        annotation = client.retrieve_annotation(aid, sideloads=["content"])

        assert annotation == Annotation(**{**dummy_annotation, "content": []})

        http_client.fetch_one.assert_called_with("annotations", aid)

    def test_poll_annotation(self, elis_client_sync, dummy_annotation):
        def is_imported(annotation):
            return annotation.status != "importing"

        client, http_client = elis_client_sync
        in_progress_annotation = {**dummy_annotation, "status": "importing"}
        # First, return annotation in importing, than to_review state
        http_client.fetch_one.side_effect = [in_progress_annotation, dummy_annotation, []]
        # Return sideloaded content
        http_client.request_json.return_value = {"content": []}

        with patch("asyncio.sleep") as sleep_mock:
            annotation = client.poll_annotation(
                dummy_annotation["id"], is_imported, sleep_s=2, sideloads=["content"]
            )

        assert annotation == Annotation(**{**dummy_annotation, "content": []})

        sleep_mock.assert_called_once_with(2)

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

        http_client.replace.assert_called_with("annotations", aid, data)

    def test_update_part_annotation(self, elis_client_sync, dummy_annotation):
        client, http_client = elis_client_sync
        http_client.update.return_value = dummy_annotation

        aid = dummy_annotation["id"]
        data = {
            "status": "deleted",
        }
        annotation = client.update_part_annotation(aid, data)

        assert annotation == Annotation(**dummy_annotation)

        http_client.update.assert_called_with("annotations", aid, data)
