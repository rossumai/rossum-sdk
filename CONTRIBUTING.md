# Contributing to Rossum SDK for Python

We welcome contributions to rossum-sdk by the community. If you are building an integration, see the [Developer Docs](https://developers.rossum.ai/) page.

## Submitting changes

* Use [`pre-commit`](https://pre-commit.com/#install) to avoid linting issues.
* Submit a pull request from forked version of this repo, referencing any issues it addresses.
* Add tests for your changes to `tests/`.
* Run tests and make sure all of them pass.
* Select any of the maintainers as a reviewer.
* After an approved review, when releasing, a `Collaborator` with `Admin` role shall do the following in `master` branch:
  * Update the Changelog, describing all the changes included in the newest release
  * Release a new version

We will review your pull request as soon as possible.
Thank you for contributing!

## Development environment

### Clone the repo

```bash
git@github.com:rossumai/rossum-sdk.git
```

Make sure that you have Python 3 installed. Version 3.8 or higher is required to run style checkers on pre-commit. On macOS, we recommend using `brew` to install Python.
For Windows, we recommend an official python.org release.

### Create a virtual environment

```bash
cd rossum-sdk

python -m venv .env

source .env/bin/activate
```

### Install `rossum-sdk` in editable mode

```bash
pip install -e .
```

### Install coding style pre-commit hooks

This will make sure that your commits will have the correct coding style.

```bash
pre-commit install

pre-commit install-hooks
```

That's it. You should be ready to make changes, run tests, and make commits!

## Running tests

We have a `Makefile` to help people get started with hacking on the SDK
without having to know or understand the Python ecosystem.
Run `make` or `make help` to list commands.

So the simplest way to run tests is:

```bash
cd rossum-sdk

make test
```

This will use [Tox](https://tox.wiki/en/latest/) to run our whole test suite
under multiple Python 3 versions.

Of course you can always run the underlying commands yourself, which is
particularly useful when wanting to provide arguments to `pytest` to run
specific tests:

```bash
cd rossum-sdk

# create virtual environment
python -m venv .env

# activate virtual environment
source .env/bin/activate

# install sentry-python
pip install -e .

# install requirements
pip install -e ."[tests]"

# run tests
pytest tests/
```
