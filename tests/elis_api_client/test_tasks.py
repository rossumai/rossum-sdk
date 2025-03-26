from __future__ import annotations

from unittest.mock import patch

import pytest

from rossum_api.domain_logic.resources import Resource
from rossum_api.models.task import Task, TaskStatus


@pytest.fixture
def dummy_task():
    return {
        "id": 16508,
        "url": "https://api.elis.master.r8.lol/v1/tasks/16508",
        "type": "upload_created",
        "status": "succeeded",
        "detail": None,
        "expires_at": "2024-07-31T19:06:47.916608Z",
        "content": {"upload": "https://api.elis.master.r8.lol/v1/uploads/37626"},
        "result_url": "https://api.elis.master.r8.lol/v1/uploads/37626",
    }


@pytest.mark.asyncio
class TestTasks:
    async def test_retrieve_task(self, elis_client, dummy_task):
        client, http_client = elis_client
        http_client.fetch_one.return_value = dummy_task

        uid = dummy_task["id"]
        task = await client.retrieve_task(uid)

        assert task == Task(**dummy_task)

        http_client.fetch_one.assert_called_with(
            Resource.Task, uid, request_params={"no_redirect": "True"}
        )

    async def test_poll_task_basic(self, elis_client, dummy_task):
        client, http_client = elis_client
        http_client.fetch_one.return_value = dummy_task

        uid = dummy_task["id"]
        task = await client.poll_task(uid, lambda a: a.status == TaskStatus.SUCCEEDED)

        assert task == Task(**dummy_task)

        http_client.fetch_one.assert_called_with(
            Resource.Task, uid, request_params={"no_redirect": "True"}
        )

    async def test_poll_task(self, elis_client, dummy_task):
        client, http_client = elis_client
        running_task = {**dummy_task, "status": TaskStatus.RUNNING}
        http_client.fetch_one.side_effect = [running_task, dummy_task.copy()]

        with patch("asyncio.sleep") as sleep_mock:
            task = await client.poll_task(
                dummy_task["id"], lambda a: a.status == TaskStatus.SUCCEEDED, sleep_s=2
            )

        assert task == Task(**{**dummy_task})

        sleep_mock.assert_called_once_with(2)


class TestTasksSync:
    def test_retrieve_task(self, elis_client_sync, dummy_task):
        client, http_client = elis_client_sync
        http_client.fetch_resource.return_value = dummy_task

        uid = dummy_task["id"]
        task = client.retrieve_task(uid)

        assert task == Task(**dummy_task)

        http_client.fetch_resource.assert_called_with(
            Resource.Task, uid, request_params={"no_redirect": "True"}
        )

    def test_poll_task_basic(self, elis_client_sync, dummy_task):
        client, http_client = elis_client_sync
        http_client.fetch_resource.return_value = dummy_task

        uid = dummy_task["id"]
        task = client.poll_task(uid, lambda a: a.status == TaskStatus.SUCCEEDED)

        assert task == Task(**dummy_task)

        http_client.fetch_resource.assert_called_with(
            Resource.Task, uid, request_params={"no_redirect": "True"}
        )

    def test_poll_task(self, elis_client_sync, dummy_task):
        client, http_client = elis_client_sync
        running_task = {**dummy_task, "status": TaskStatus.RUNNING}
        http_client.fetch_resource.side_effect = [running_task, dummy_task.copy()]

        with patch("time.sleep") as sleep_mock:
            task = client.poll_task(
                dummy_task["id"], lambda a: a.status == TaskStatus.SUCCEEDED, sleep_s=2
            )

        assert task == Task(**{**dummy_task})

        sleep_mock.assert_called_once_with(2)
