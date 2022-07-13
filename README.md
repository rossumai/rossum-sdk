README
======

[![PyPI - version](https://img.shields.io/pypi/v/rossum.svg)](https://pypi.python.org/pypi/rossum)
[![Build Status](https://travis-ci.com/rossumai/rossum.svg?branch=master)](https://travis-ci.com/rossumai/rossum)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![codecov](https://codecov.io/gh/rossumai/rossum/branch/master/graph/badge.svg)](https://codecov.io/gh/rossumai/rossum)
![PyPI - supported python versions](https://img.shields.io/pypi/pyversions/rossum.svg)
![MIT licence](https://img.shields.io/pypi/l/rossum.svg)


**rossum-sdk** is a Python package delivering programmatic access to the [Rossum API](https://api.elis.rossum.ai/docs). This package is focused on accessing HTTP API only, if you need more advanced usage like Schema Transformations or interactive CLI tool, please refer to [Rossum package](https://github.com/rossumai/rossum).

## Installation
The easiest way is to install the package from PyPI:
```bash
pip install rossum-sdk
```

You can eventually download an installation file from
[GitHub releases](https://github.com/rossumai/rossum-sdk/releases).
and install it manually.


## Usage
### Python API SDK
The **rossum-sdk** library can be used to communicate with Rossum API,
instead of using `requests` library directly. The advantages of using **rossum-sdk**:
* it contains a function that merges the paginated results into one list so the user does not need
to get results page by page and take care of their merging,
* it comes with both synchronous and asynchronous API, so you can choose the flavour you need,
* it takes care of authenticating the user,
* it includes many methods for frequent actions that you don't need to write by yourself from scratch,
* it returns the result as a Python first class object - Dataclass, so you don't need to parse the JSON by yourself,
* it maps method naming as close as possible to [API docs](https://elis.rossum.ai/api/docs),
* in case the API version changes, the change will be implemented to the
library by Rossum for all the users.


### Examples
You can choose between asynchronous and synchronous client. Both are exactly the same in terms of features. If you try to use synchronous client in the environment, where event loop is already present and running (for example Jupyter Notebook), exception will be thrown advising to use the async version.

Async version:
```python
import asyncio
from rossum_ng.elis_api_client import ElisAPIClient

WORKSPACE = {
    "name": "Rossum Client NG Test",
    "organization": "https://elis.develop.r8.lol/api/v1/organizations/116390",
}

async def main_with_async_client():
    client = ElisAPIClient(
        os.environ["ELIS_USERNAME"],
        os.environ["ELIS_PASSWORD"],
        base_url="https://elis.develop.r8.lol/api/v1",
    )
    ws = await client.create_new_workspace(data=WORKSPACE)
    workspace_id = ws.id
    ws = await client.retrieve_workspace(workspace_id)
    print("GET result:", ws)
    print("LIST results:")
    async for w in client.list_all_workspaces(["-id"], None, name=WORKSPACE["name"]):
        print(w)
    await client.delete_workspace(workspace_id)
    print(f"Workspace {workspace_id} deleted.")

asyncio.run(main_with_async_client())
```

Sync version:
```python
from rossum_ng.elis_api_client_sync import ElisAPIClientSync

WORKSPACE = {
    "name": "Rossum Client NG Test",
    "organization": "https://elis.develop.r8.lol/api/v1/organizations/116390",
}

def main_with_sync_client():
    client = ElisAPIClientSync(
        os.environ["ELIS_USERNAME"],
        os.environ["ELIS_PASSWORD"],
        base_url="https://elis.develop.r8.lol/api/v1",
    )
    ws = client.create_new_workspace(data=WORKSPACE)
    workspace_id = ws.id
    ws = client.retrieve_workspace(workspace_id)
    print("GET result:", ws)
    print("LIST results:")
    for w in client.list_all_workspaces(["-id"], None, name=WORKSPACE["name"]):
        print(w)
    client.delete_workspace(workspace_id)
    print(f"Workspace {workspace_id} deleted.")

main_with_sync_client()
```

## License
MIT

## Contributing

* Use [`pre-commit`](https://pre-commit.com/#install) to avoid linting issues.
* Submit a pull request from forked version of this repo.
* Select any of the maintainers as a reviewer.
* After an approved review, when releasing, a `Collaborator` with `Admin` role shall do the following in `master` branch:
* **TODO**
