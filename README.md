# Rossum SDK

[![Build Status](https://github.com/rossumai/rossum-sdk/actions/workflows/test-and-deploy.yaml/badge.svg)](https://github.com/rossumai/rossum-sdk/actions)
[![Coverage](https://codecov.io/gh/rossumai/rossum-sdk/branch/main/graph/badge.svg)](https://codecov.io/gh/rossumai/rossum-sdk)
[![Code style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![PyPI version](https://img.shields.io/pypi/v/rossum-api.svg)](https://pypi.org/project/rossum-api/)
![MIT licence](https://img.shields.io/pypi/l/rossum.svg)

**rossum-sdk** is a repository for libraries useful when integrating Rossum platform into other Python applications. The following packages are provided:


* `rossum-api` – delivers programmatic access to the [Rossum API](https://api.elis.rossum.ai/docs).
  * This package is focused on accessing HTTP API only, if you need more advanced usage like Schema Transformations or interactive CLI tool, please refer to [Rossum package](https://github.com/rossumai/rossum).


## rossum-api

### Installation

The easiest way is to install the package from PyPI:

```bash
pip install rossum-api
```

or from the github repo:
```bash
pip install git+https://github.com/rossumai/rossum-sdk#egg=rossum-api
```

You can eventually download an installation file from [GitHub releases](https://github.com/rossumai/rossum-sdk/releases).
and install it manually.

### Usage

#### Python API SDK

The **rossum-api** library can be used to communicate with Rossum API, instead of using `requests` library directly. The advantages of using **rossum-sdk**:

* it contains a function that merges the paginated results into one list so the user does not need to get results page by page and take care of their merging,
* it comes with both synchronous and asynchronous API, so you can choose the flavour you need,
* it takes care of authenticating the user,
* it includes many methods for frequent actions that you don't need to write by yourself from scratch,
* it returns the result as a Python first class object - Dataclass, so you don't need to parse the JSON by yourself,
* it maps method naming as close as possible to [API docs](https://elis.rossum.ai/api/docs),
* in case the API version changes, the change will be implemented to the library by Rossum for all the users.
* it has minimal dependencies

#### Examples

You can choose between asynchronous and synchronous client. Both are exactly the same in terms of features. If you try to use synchronous client in the environment, where event loop is already present and running (for example Jupyter Notebook), exception will be thrown advising to use the async version.

Async version:

```python
import os
import asyncio
from rossum_api import AsyncRossumAPIClient
from rossum_api.dtos import UserCredentials

WORKSPACE = {
  "name": "Rossum Client NG Test",
  "organization": "https://elis.rossum.ai/api/v1/organizations/116390",
}


async def main_with_async_client():
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
```

Sync version:

```python
import os
from rossum_api import SyncRossumAPIClient
from rossum_api.dtos import UserCredentials

WORKSPACE = {
    "name": "Rossum Client NG Test",
    "organization": "https://elis.rossum.ai/api/v1/organizations/116390",
}


def main_with_sync_client():
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
```

### Local development

Pull the repository, create a virtual environment, and install the package from the source with test dependencies:
```bash
# Create and activate virtual environment
python -m venv .env
source .env/bin/activate

# Install in editable mode with test dependencies
pip install -e .[tests]
```

We use ruff for linting and formatting. Run all pre-commit hooks with:
```bash
pre-commit run --all-files
```

Or run specific tools:
```bash
# Linting and formatting
pre-commit run ruff --all-files
pre-commit run ruff-format --all-files

# Type checking
pre-commit run mypy --all-files

# Run tests
pytest
```

## License

MIT
