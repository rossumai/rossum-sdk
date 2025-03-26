from rossum_api.dtos import UserCredentialsfrom rossum_api.dtos import UserCredentials

# Rossum SDK

[![Build Status](https://github.com/rossumai/rossum-sdk/actions/workflows/lint-and-test.yaml/badge.svg)](https://github.com/rossumai/rossum-sdk/actions)
[![Coverage](https://codecov.io/gh/rossumai/rossum-sdk/branch/main/graph/badge.svg)](https://codecov.io/gh/rossumai/rossum-sdk)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
![MIT licence](https://img.shields.io/pypi/l/rossum.svg)

**rossum-sdk** is a repository for libraries useful when integrating Rossum platform into other Python applications. The following packages are provided:


* `rossum-api` – delivers programmatic access to the [Rossum API](https://api.elis.rossum.ai/docs).
  * This package is focused on accessing HTTP API only, if you need more advanced usage like Schema Transformations or interactive CLI tool, please refer to [Rossum package](https://github.com/rossumai/rossum).


## rossum-api

### Installation

The easiest way is to install the package from PyPI:

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

### Development

There is a `Makefile` that can help you setup a development environment quickly, run the following commands

```
make .venv  # Creates virtualenv in .venv folder
make install # Installs all project dependencies including test ones
```

Run `make help` to see more available actions.

### TODO

* convert datetimes to ISO 8601 string in `APIClient` to allow users passing standard datetime objects
* implement password reset
* rate limiting?

## License

MIT
