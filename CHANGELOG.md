# CHANGELOG


## v3.6.0 (2025-11-10)

### Features

- Add Rule & Rule Actions
  ([`76280c6`](https://github.com/rossumai/rossum-api/commit/76280c6f503972bdf497c0de773ea3c18e22433a))


## v3.5.2 (2025-11-06)

### Bug Fixes

- Fix README path in pyproject
  ([`bdd1f47`](https://github.com/rossumai/rossum-api/commit/bdd1f47ff8fad04f8fb7ee7ec151a99a17b0d31e))


## v3.5.1 (2025-11-06)

### Bug Fixes

- Fix readme symlink direction and badges
  ([`58e89ee`](https://github.com/rossumai/rossum-api/commit/58e89ee78bad9b213b64b735fd28a76b0a9f7714))

### Documentation

- Add documentation deployment CI step
  ([`2f7d144`](https://github.com/rossumai/rossum-api/commit/2f7d144e8a71fb738d4d77739e0250f84d8978ec))

- Add link and badge with link to docs
  ([`9712884`](https://github.com/rossumai/rossum-api/commit/9712884d06cb9d359476e7aeb608cf52d8a2be18))

- Build docs to docs/build instead of docs/build
  ([`18f8eea`](https://github.com/rossumai/rossum-api/commit/18f8eea5021ed875cf6057f300f241620c542ace))

- Fix forgotten uv --sytem option
  ([`b22593f`](https://github.com/rossumai/rossum-api/commit/b22593f2fb72626e4ef4621db8e4315017852b2e))

- Simplify and merge docs build and deploy workflows
  ([`00ddf90`](https://github.com/rossumai/rossum-api/commit/00ddf90fed7b0bc8db6fef279d15db060c88d626))


## v3.5.0 (2025-11-06)

### Chores

- Fix missing semantic release coment in chlog
  ([`2629e3b`](https://github.com/rossumai/rossum-api/commit/2629e3bab410b4cb5d165563d3e33e1ebaf44abd))

- Introduce all pyupgrade rules
  ([`c02a21b`](https://github.com/rossumai/rossum-api/commit/c02a21b5cab773d0430c9197c826c52b3ba032f1))

- Introduce all RET ruff rules
  ([`897ea4c`](https://github.com/rossumai/rossum-api/commit/897ea4c3e067c78c9c794d039ee97b421af5753c))

- Introduce all RUF ruff rules
  ([`ea9641e`](https://github.com/rossumai/rossum-api/commit/ea9641e8bffd41cafa56341a99b016bc3e182581))

- Introduce all S (flake8-bandit) ruff rules
  ([`7197383`](https://github.com/rossumai/rossum-api/commit/7197383e2bd8b4e1453d097df71555ed7de09a89))

- Introduce all SIM ruff rules
  ([`3959ec3`](https://github.com/rossumai/rossum-api/commit/3959ec3cc220b4c968cfcfdd6a4966d5d536417e))

- Set semantic release to re-generate full chlog
  ([`edabd78`](https://github.com/rossumai/rossum-api/commit/edabd7847045f19bac5e83e7c118de7ec91ca9fa))

- Update and pin ci action versions
  ([`28822db`](https://github.com/rossumai/rossum-api/commit/28822dbfa3a857226f7da7225547d5014cce8de4))

### Documentation

- Introduce sphinx docs
  ([`4505029`](https://github.com/rossumai/rossum-api/commit/4505029ff6561308dd0ed050f9d4204eacb66fcd))

- Update docs to Rossum API only
  ([`ecda8c8`](https://github.com/rossumai/rossum-api/commit/ecda8c8a76f10e70eb82bed931a631b6459570da))

### Features

- Achieve feature parity across sync and async clients
  ([`9cc7846`](https://github.com/rossumai/rossum-api/commit/9cc7846797cfbe4732aa9f7b1db25df07f8138d4))


## v3.4.0 (2025-10-30)

### Chores

- Add basic pre-commit hooks
  ([`87aff93`](https://github.com/rossumai/rossum-api/commit/87aff935f87ef8cfa496e6d66b79676e26927770))

- Define Sideload as a type
  ([`c639b7a`](https://github.com/rossumai/rossum-api/commit/c639b7a624065c9a48c35320f90c8eef4c5d3b23))

- Enforce PEP 585
  ([`eed9f47`](https://github.com/rossumai/rossum-api/commit/eed9f47766b037843ece82597440556faff9b23c))

- Enforce PEP 604
  ([`118bb97`](https://github.com/rossumai/rossum-api/commit/118bb97eb5329172f9c4422add1c2e314af83a6d))

- Enforce PEP 604 for optional types
  ([`118d968`](https://github.com/rossumai/rossum-api/commit/118d96854e06a05766008fe5077e7227690bacc9))

- Enforce TCH rule
  ([`ffd68de`](https://github.com/rossumai/rossum-api/commit/ffd68de951ddc5ac4547c200557fe5a3205963af))

- Enforce type checking and fix typing
  ([`cae0ecd`](https://github.com/rossumai/rossum-api/commit/cae0ecdc6544a7ae428723086a7f652af20be174))

- Fix typo in LICENSE file name
  ([`f10b56d`](https://github.com/rossumai/rossum-api/commit/f10b56df10439320af2f93ebfc1a8c9fb420a328))

- Publish package automatically to pypi upon release
  ([`c335845`](https://github.com/rossumai/rossum-api/commit/c33584556e7a97c672be1fdfbf7d9db13574129d))

- Remove unused .flake8 file
  ([`ade9ea7`](https://github.com/rossumai/rossum-api/commit/ade9ea792bcc6a8d06c83fd139b521352ef76a61))

- Remove unused black and isort configs from pyproject.toml
  ([`80bf6f9`](https://github.com/rossumai/rossum-api/commit/80bf6f9c36f216f892c960e9931173011ad2b11f))

- Remove unused Makefile
  ([`24b4e8e`](https://github.com/rossumai/rossum-api/commit/24b4e8e611d822fadf22a678c366b8be17dd908f))

- Remove unused tox.ini file
  ([`11da97f`](https://github.com/rossumai/rossum-api/commit/11da97ff797504b91bd8766705710e7a46597e26))

- Save a few lines by cleaning trailing commas
  ([`cda1933`](https://github.com/rossumai/rossum-api/commit/cda1933f0636bddb44de38ec21fc145e469be2bf))

- Start using ruff in its full strength
  ([`3d5becd`](https://github.com/rossumai/rossum-api/commit/3d5becd04b367883cdd948234bbbe4dfa2ac613e))

- Unify absolute imports of models
  ([`59b4c03`](https://github.com/rossumai/rossum-api/commit/59b4c0366a06680af21f6a6f41a0b182dba4bd0b))

- Update package version in pre-commit
  ([`0781db4`](https://github.com/rossumai/rossum-api/commit/0781db497c37d61cebd6b5aba89872a6a6f2e876))

- Use JsonDict type globally
  ([`44b9b8a`](https://github.com/rossumai/rossum-api/commit/44b9b8a4e9c55b0db7936f66a72959abb94a545b))

### Documentation

- Add badge to pypi
  ([`ef6e6d4`](https://github.com/rossumai/rossum-api/commit/ef6e6d486f49207032532fd2b6f2f1d5f01da7c0))

- Add local development section to README
  ([`bc6062c`](https://github.com/rossumai/rossum-api/commit/bc6062cdf47b58ed2b29383a8a99735a848706b9))

- Clean CONTRIBUTING.md
  ([`033e7a3`](https://github.com/rossumai/rossum-api/commit/033e7a38873cce07d2fa49b7f2e68ba4acc69d74))

- Fix badges
  ([`191250d`](https://github.com/rossumai/rossum-api/commit/191250dfdbe1fe4b5994dba8a00f69643b9db3a5))

- Fix unintentional copy to README
  ([`2f6e13b`](https://github.com/rossumai/rossum-api/commit/2f6e13bd31f9bb0403a3890c2b4ffdd1c9419a80))

- Regenerate CHANGELOG.md following semantic releases conventions
  ([`f008e54`](https://github.com/rossumai/rossum-api/commit/f008e54738392b8d9885f4629a73261529872a2a))

- Remove TODO list
  ([`3f1c9b4`](https://github.com/rossumai/rossum-api/commit/3f1c9b4da74e57bf6423e74bd0b4165bf2128b7d))

- Update installation guide
  ([`924d108`](https://github.com/rossumai/rossum-api/commit/924d108dfd56826aab1e228e47d8d5761bb7d64c))

### Features

- Replace heavy inflect import by a simple heuristic
  ([`683e722`](https://github.com/rossumai/rossum-api/commit/683e72279fc4c0af2753264331f04ef99725a6aa))


## v3.3.0 (2025-10-27)

### Chores

- Replace python <=3.9 support with python 3.13
  ([`d3dc4bf`](https://github.com/rossumai/rossum-api/commit/d3dc4bfde7c3e967edde314dff36d0bcf51ce329))

- Upgrade pytest-httpx
  ([`59326f1`](https://github.com/rossumai/rossum-api/commit/59326f1fc6dd4fb1ee725537f8d600a80f191896))

### Features

- Add training_queues field for Engine
  ([`6099877`](https://github.com/rossumai/rossum-api/commit/60998778b4859bc08d5a91f170aaa88cfb0da20d))


## v3.2.0 (2025-09-16)

### Features

- Add authenticate method to Rossum API client
  ([`9bc0d86`](https://github.com/rossumai/rossum-api/commit/9bc0d86b035967205f7b847f90b2f13a7907d425))


## v3.1.3 (2025-09-10)

### Bug Fixes

- Fix sideload in sync client
  ([`e140569`](https://github.com/rossumai/rossum-api/commit/e140569066e54578a61aa76fe99d4c10018a2166))


## v3.1.2 (2025-09-08)

### Bug Fixes

- Switch from token header to Bearer auth and update tests
  ([`45ed114`](https://github.com/rossumai/rossum-api/commit/45ed114a0ebba1f9a7c9912deef1181f410b2cd9))

- Switch from token header to Bearer auth and update tests (+ Sync client)
  ([`20d715b`](https://github.com/rossumai/rossum-api/commit/20d715b0bb9eb326bfb39508fd25465ce727f003))


## v3.1.1 (2025-06-27)

### Bug Fixes

- Use venv pytest for the test command
  ([`fb24918`](https://github.com/rossumai/rossum-api/commit/fb24918063ef949d3786acc0e21dd7387ba4d7e2))


## v3.1.0 (2025-06-06)

### Features

- Add einvoice document relation type
  ([`2396694`](https://github.com/rossumai/rossum-api/commit/2396694ec085d11aae89489864c8bc1aec5c91ea))


## v3.0.0 (2025-05-28)

### Bug Fixes

- Make Task.content optional
  ([`48d1e4d`](https://github.com/rossumai/rossum-api/commit/48d1e4dcd20a6be1d69b36424ede3c6cc86f90a7))

### Features

- Add email resource
  ([`4b2509b`](https://github.com/rossumai/rossum-api/commit/4b2509ba10256b3ad1a28e72e675f80457e5f6d3))

- Add email_imported task type
  ([`a1db151`](https://github.com/rossumai/rossum-api/commit/a1db15126262f580b04e37c52aa8b5b6be03b685))

### Breaking Changes

- Adding to Generic class can break existing setups.


## v2.1.0 (2025-05-28)

### Features

- Add missing annotation fields
  ([`71c2e2d`](https://github.com/rossumai/rossum-api/commit/71c2e2d732da01a5ff1b1d3bc6542f763f008d7e))


## v2.0.1 (2025-04-28)

### Bug Fixes

- Move exceptions module to rossum_api package
  ([`548215a`](https://github.com/rossumai/rossum-api/commit/548215a4bf04934ba0b80eb8078da314202d92d3))


## v2.0.0 (2025-04-24)

### Features

- Add document relation resource
  ([`230bb1c`](https://github.com/rossumai/rossum-api/commit/230bb1c8be1f25be9a0f844a831ce2600bedcfa7))

### Breaking Changes

- Adding to Generic class can break existing setups.


## v1.0.1 (2025-04-04)

### Bug Fixes

- Fix bugs in internal sync client
  ([`5e57018`](https://github.com/rossumai/rossum-api/commit/5e57018b5f2a99b3f37cfe5045d2a2b538432471))

### Refactoring

- Rename module with tests of internal async client
  ([`1334338`](https://github.com/rossumai/rossum-api/commit/1334338ab372d2e7313fcf12961cb442892007e0))

- Use helpers from domain logic in clients
  ([`24e0657`](https://github.com/rossumai/rossum-api/commit/24e0657a131aa3629596b582e41dcca04580197f))


## v1.0.0 (2025-03-26)

### Features

- Implement sync client without event loop
  ([`3964632`](https://github.com/rossumai/rossum-api/commit/3964632e9fd112cef5bc8c8c001ef39398fff48f))

### Breaking Changes

- Public interface changed.


## v0.24.0 (2025-03-21)

### Features

- Add response post-processor
  ([`a1ab75f`](https://github.com/rossumai/rossum-api/commit/a1ab75fe505af59ffb363b69439abc4596a156bb))


## v0.23.2 (2025-03-20)

### Bug Fixes

- Resolve problem with typing and custom deserializer
  ([`a9b95bd`](https://github.com/rossumai/rossum-api/commit/a9b95bd16bb2df227727cc30b52d3189ed97f0e9))


## v0.23.1 (2025-01-23)

### Bug Fixes

- Rename retrieve_engine_queue_stats to retrieve_engine_queues
  ([`7583358`](https://github.com/rossumai/rossum-api/commit/7583358da05b37f822e60f9c7b440064d20fbe7c))


## v0.23.0 (2025-01-20)

### Features

- Add more information to APIClientError
  ([`53d0781`](https://github.com/rossumai/rossum-api/commit/53d07810ccad959a3d110f622c8c46316a374a01))

- Add support for filters in export helper methods
  ([`8a94d6f`](https://github.com/rossumai/rossum-api/commit/8a94d6fbba26ed9db1c59499577f93d53a252d36))


## v0.22.0 (2025-01-16)

### Bug Fixes

- Remove 'button' possibility for EngineField.type as it should not happen
  ([`da698b0`](https://github.com/rossumai/rossum-api/commit/da698b01ef2438ebe658dc7e6e67a5b48a60ec81))

- Use _iter_over_async instead of _run_coroutine and Iterator instead of list
  ([`9540929`](https://github.com/rossumai/rossum-api/commit/95409299c468e28a4d89e2a90646d9d2aa73a33e))

### Code Style

- Reformat method parameters - do not break lines if not necessary
  ([`31537af`](https://github.com/rossumai/rossum-api/commit/31537af555c87f2f3563135692e6530d384e42a3))

### Features

- Support retrieval of Queues associated with the given Engine
  ([`8aee3d4`](https://github.com/rossumai/rossum-api/commit/8aee3d43a52a8d18bbdb19746675050a7efa89b8))


## v0.21.0 (2025-01-14)

### Chores

- Correct resource name in sideloading test integration test
  ([`a419002`](https://github.com/rossumai/rossum-api/commit/a4190024be69ec2f61ab533abee23415598240ec))

### Features

- Add support for retrieving EngineFields
  ([`c976954`](https://github.com/rossumai/rossum-api/commit/c976954d35369ab3f03b40861093f5ff257ec5a4))

### Refactoring

- Extract sideloading logic into domain logic
  ([`080b7af`](https://github.com/rossumai/rossum-api/commit/080b7afbb2f1a7ec3651ee80a6561c9921c55aaf))


## v0.20.1 (2024-12-11)

### Bug Fixes

- Prevent race condition over the asyncio event loop in ThreadPoolExecutor
  ([`6a4d922`](https://github.com/rossumai/rossum-api/commit/6a4d922f9ebe98aa82ab2395f4b62c749eb89c10))

### Chores

- Extract Resource into domain logic
  ([`99ec60c`](https://github.com/rossumai/rossum-api/commit/99ec60c1fa51dccc684b600b976608807b681e5b))

- Extract URL domain logic into a reusable module
  ([`826fcd5`](https://github.com/rossumai/rossum-api/commit/826fcd5e766bde55f6f4bfc991a22ce422cac7dd))


## v0.20.0 (2024-12-10)

### Bug Fixes

- Do not crash when running sync client in async context
  ([`0038e4a`](https://github.com/rossumai/rossum-api/commit/0038e4a3bfe2f2312a4dfb91f0a7988ba1c798ac))

### Chores

- Fix tests by pinning pytest-httpx
  ([`a0c0eeb`](https://github.com/rossumai/rossum-api/commit/a0c0eeb85334f9c3bd86e599ab01c26f5c3bf275))

- Improve readability of assert in XML export test
  ([`4c88b7e`](https://github.com/rossumai/rossum-api/commit/4c88b7e4328f01035a5c9f64ab4b013cce82bb73))

### Features

- Retry also on request/HTTP errors during authentication
  ([`3bae7da`](https://github.com/rossumai/rossum-api/commit/3bae7dad7d045faad0caf1a038aaf6d0400cbe47))


## v0.19.0 (2024-09-25)

### Chores

- Fix naming in queues tests
  ([`2c51b64`](https://github.com/rossumai/rossum-api/commit/2c51b640124394cb86c85e23546d0dd591ecfdf9))

### Features

- Add cancel annotation method
  ([`a217b64`](https://github.com/rossumai/rossum-api/commit/a217b64dc4609bca144322a5fe93dff26b0ff752))

- Add new methods for hook object
  ([`232269f`](https://github.com/rossumai/rossum-api/commit/232269fe8582c4d553172f510265a0b8cbccfaff))

- Add retrieve document method
  ([`4edac76`](https://github.com/rossumai/rossum-api/commit/4edac76684b0ac9cb8146dafaa1f92214bfe02e1))


## v0.18.1 (2024-08-20)

### Bug Fixes

- Handle http:// urls for local development
  ([`715513d`](https://github.com/rossumai/rossum-api/commit/715513d8144c8ede02d7288788fd73ca5722a2e3))


## v0.18.0 (2024-08-15)

### Features

- Add basic support for EmailTemplate object
  ([`0dc2882`](https://github.com/rossumai/rossum-api/commit/0dc28825f9f76e4f8bd6f10742f23ebf10633025))


## v0.17.2 (2024-08-12)

### Bug Fixes

- Fix typing of filters kwargs in sync client
  ([`7ae75e1`](https://github.com/rossumai/rossum-api/commit/7ae75e1bb335f0c52656982315eb4d39f5b84a62))


## v0.17.1 (2024-08-09)

### Bug Fixes

- Use Iterator instead of Iterable types
  ([`77edb52`](https://github.com/rossumai/rossum-api/commit/77edb529e4b69c74695bc16516cfe27ba9094c01))


## v0.17.0 (2024-08-07)

### Chores

- Drop support for Python 3.7
  ([`3a4e359`](https://github.com/rossumai/rossum-api/commit/3a4e359c5e7df7c22ef92a64be3369814c8f4e1d))

- Fix typos and missing docs
  ([`a499da2`](https://github.com/rossumai/rossum-api/commit/a499da214b01cb4fc1b433c7708cd66320a62ae1))

### Features

- Add support for Task and Upload objects
  ([`6e582a9`](https://github.com/rossumai/rossum-api/commit/6e582a9451ffd95950442fd6bda7af8a80df0e39))

- Upload documents using new upload endpoint
  ([`9ff22d9`](https://github.com/rossumai/rossum-api/commit/9ff22d9340210f1d2fde5c0a5b8894f578eaad82))


## v0.16.0 (2024-06-04)

### Chores

- Add missing type hint for list_all_organizations
  ([`86fb228`](https://github.com/rossumai/rossum-api/commit/86fb228613aa60a0b48c04a1549252454d15b2c9))

### Features

- Add delete_annotation method ([#75](https://github.com/rossumai/rossum-api/pull/75),
  [`55a3641`](https://github.com/rossumai/rossum-api/commit/55a364100e73ec24da009b12819830c7dbd69e5a))


## v0.15.2 (2024-06-03)

### Bug Fixes

- Fix package versioning
  ([`d3b5e88`](https://github.com/rossumai/rossum-api/commit/d3b5e889d2b4045c63e16eda961922a734b6db66))


## v0.15.1 (2024-06-03)

### Bug Fixes

- Remove semantic-release version_variable
  ([`9d5d101`](https://github.com/rossumai/rossum-api/commit/9d5d101016f31d54c612be5a79ba93a0eb6a59f2))


## v0.15.0 (2024-06-03)

### Features

- Add support for engine object
  ([`c6ad1d5`](https://github.com/rossumai/rossum-api/commit/c6ad1d5809f08113dff074120fa55e8673218de5))


## v0.14.0 (2024-05-22)

### Features

- Add py.typed and let the world know we use types
  ([`9415403`](https://github.com/rossumai/rossum-api/commit/941540354521e321c2e40cc12b3b2a6e24a8abce))


## v0.13.3 (2024-05-22)

### Bug Fixes

- Make User.last_login optional
  ([`406b16b`](https://github.com/rossumai/rossum-api/commit/406b16bdf7528073f1e453a7d2ef7cb4777b4191))


## v0.13.2 (2024-04-09)

### Bug Fixes

- **api-client**: Do not reauth if no credentials are available
  ([`9b5f422`](https://github.com/rossumai/rossum-api/commit/9b5f4223b3f1ac852315e98956c920cb16aebd21))


## v0.13.1 (2024-03-25)

### Bug Fixes

- **models:automation_blocker**: Fix type of `samples`
  ([`b36d6a8`](https://github.com/rossumai/rossum-api/commit/b36d6a8f1b3ae46722bb5dacf0d01fed5d2544b4))

### Continuous Integration

- **pre-commit**: Update mypy
  ([`06d2272`](https://github.com/rossumai/rossum-api/commit/06d22725d0a9a33ade3d700779707e7c955268dd))


## v0.13.0 (2024-02-07)

### Bug Fixes

- Do not send None parent when creating new document
  ([`95f3fbc`](https://github.com/rossumai/rossum-api/commit/95f3fbca22d6ca157567ccf71bd3ff379ab29705))

### Documentation

- Improve client docstrings
  ([`94e8522`](https://github.com/rossumai/rossum-api/commit/94e85229ee3f64bd169ac79c2a8a3a2bf0f03996))

### Features

- Consider new created status when checking if annotation is already imported
  ([`7c66c63`](https://github.com/rossumai/rossum-api/commit/7c66c63585e35cf58272253ba143003c053dccff))


## v0.12.0 (2024-02-06)

### Features

- Add new create_new_annotation method
  ([`7354ec7`](https://github.com/rossumai/rossum-api/commit/7354ec71fd7f821ac92870ada87ce44b935fb2c5))

- Add new create_new_document method
  ([`4affb67`](https://github.com/rossumai/rossum-api/commit/4affb6704072305637b5fec403fe3993e0ee1cf3))

- Add new retrieve_document_content method
  ([`4057e9c`](https://github.com/rossumai/rossum-api/commit/4057e9c170267302d7b740980a91c7af26e044ef))

### Refactoring

- Unify naming of ids and add missing typing
  ([`86246cd`](https://github.com/rossumai/rossum-api/commit/86246cd612336f1d919cb01a06f5ea5b542c20fd))

- **tests**: Fix typos in tests
  ([`19711e2`](https://github.com/rossumai/rossum-api/commit/19711e233752c0d2102e4ae4633a3ffdff88a05c))


## v0.11.0 (2023-11-08)

### Chores

- Remove side-effects from tests with sideloads
  ([`c3f8130`](https://github.com/rossumai/rossum-api/commit/c3f8130561815f1a8f26d7f25a557e77f9e625b3))

### Features

- Add convenience methods for annotation lifecycle
  ([`cf56272`](https://github.com/rossumai/rossum-api/commit/cf56272354634a5002030c977ac295b72a15a3aa))

### Refactoring

- Rename UserRole to Group for consistency with the API
  ([`ed8065a`](https://github.com/rossumai/rossum-api/commit/ed8065a5abda3a69e3f8347626e63d67ad5f4c5d))


## v0.10.0 (2023-11-02)

### Chores

- Streamline Makefile and improve README
  ([`0b1064f`](https://github.com/rossumai/rossum-api/commit/0b1064f74fd2a60ce3c5a5fc6cde6194a3413907))

### Features

- Support deserializing of API payloads to user-defined model classes
  ([`a1e1385`](https://github.com/rossumai/rossum-api/commit/a1e1385649d974637bec33bd920705d0cdb56f2f))

### Refactoring

- Use an enum instead of strings to identify API resources
  ([`acbf731`](https://github.com/rossumai/rossum-api/commit/acbf731d369b0adfd2da9268008ca458848a20b1))


## v0.9.1 (2023-10-11)

### Bug Fixes

- **api_client**: Limit in-flight requests
  ([`56244d0`](https://github.com/rossumai/rossum-api/commit/56244d07569ad075ecd4703c3794a344eb609acd))


## v0.9.0 (2023-10-11)

### Features

- Export public interface in root package
  ([`f85fc58`](https://github.com/rossumai/rossum-api/commit/f85fc58f017b5108b46819af8cf592e34de3f3e5))


## v0.8.0 (2023-08-25)

### Features

- **api_client**: Allow passing json argument in `fetch_all` as request payload
  ([`e433f85`](https://github.com/rossumai/rossum-api/commit/e433f858bbca35c7cf3211a7dabbbea921ec431d))

- **elis_api_clients**: Add new `search_for_annotations` method
  ([`34b3f72`](https://github.com/rossumai/rossum-api/commit/34b3f7249c149d0fa2da6fa1a171b92f0a0a2ffa))


## v0.7.4 (2023-08-11)

### Features

- **models**: Add token_lifetime_s attribute to hook model
  ([`f75dcfd`](https://github.com/rossumai/rossum-api/commit/f75dcfd5d346edadef9e56532316b217d069fbbb))


## v0.7.3 (2023-08-07)

### Bug Fixes

- Make time_spent in Annotation optional
  ([`a2e5d70`](https://github.com/rossumai/rossum-api/commit/a2e5d70a777b2c2fb0fc77b78eb005311cd36853))


## v0.7.2 (2023-06-02)

### Bug Fixes

- Add await to asyncio.sleep
  ([`4a537ab`](https://github.com/rossumai/rossum-api/commit/4a537ab6641e7745383a45dba7dd77bc0d6eb28c))


## v0.7.1 (2023-05-05)

### Bug Fixes

- **models**: Allow Any in metadata dict values in Queue model
  ([`7abaa13`](https://github.com/rossumai/rossum-api/commit/7abaa135a5f5f30f6e001afa9d22258dc89fcbc1))

- **models**: Allow null workspace in Queue model
  ([`dea0027`](https://github.com/rossumai/rossum-api/commit/dea00275c23d8b121ad29c1e624e74431923a4b0))


## v0.7.0 (2023-05-04)

### Features

- **elis_api_client**: Add generic method for requests to paginated resources
  ([`6b290e8`](https://github.com/rossumai/rossum-api/commit/6b290e8cb340f7be81768b311678163a3bfc41a8))


## v0.6.0 (2023-04-28)

### Chores

- Run test workflow also on pull requests
  ([`0ca9b43`](https://github.com/rossumai/rossum-api/commit/0ca9b43a555fbf3e238867a538e1459581351a74))

### Features

- **api_client**: Allow to set max pages limit in filters
  ([`090114f`](https://github.com/rossumai/rossum-api/commit/090114fbaecc3d84706715e80f119e623882826a))


## v0.5.1 (2023-03-31)

### Bug Fixes

- Switch from TravisCI to Github Workflows
  ([`de09e69`](https://github.com/rossumai/rossum-api/commit/de09e698f20c587932d5ad050d68f96e043ad645))

### Chores

- Fix semantic release
  ([`f1e56a5`](https://github.com/rossumai/rossum-api/commit/f1e56a57ac9d0210b5e3258ae71d63950c5598d1))


## v0.5.0 (2023-03-06)

### Features

- **rossum_sdk/api_client**: Add `request` method to ElisApiClient
  ([`5d11c3e`](https://github.com/rossumai/rossum-api/commit/5d11c3e5e70e22f2875787b8ee960b8184ddb99d))


## v0.4.0 (2023-03-02)

### Bug Fixes

- Define `Document.creator` as optional ([#35](https://github.com/rossumai/rossum-api/pull/35),
  [`d797e99`](https://github.com/rossumai/rossum-api/commit/d797e99112416602487409aaa668327fd80663aa))

- **models:hook**: Define some attributes (guide, read_more_url, extension_image_url) as optional
  ([`b16a456`](https://github.com/rossumai/rossum-api/commit/b16a456344b41908c16c32b4d5be70d31f3b07b3))

### Chores

- Add pre-commit hook for commit messages
  ([`e641469`](https://github.com/rossumai/rossum-api/commit/e6414696a7cd9405978c2afd0a3aa050ee7fc9e6))

- Do not run commitizen when there is no commit
  ([`4f534d5`](https://github.com/rossumai/rossum-api/commit/4f534d55f8b6dd1bd981c3fe8aa1c00c36af493e))

- Fix mypy installation in pre-commit by upgrading it
  ([`5d4b387`](https://github.com/rossumai/rossum-api/commit/5d4b3870570cd7fcd82e86c8835246e7733e29ed))

- Fix tests that started failing with pytest-httpx==0.21.2
  ([`da18d27`](https://github.com/rossumai/rossum-api/commit/da18d275eebc4f85af8a6c6f913f430e8e1b871c))

- Run semrel only once
  ([`3b9392a`](https://github.com/rossumai/rossum-api/commit/3b9392ab7cbcbe049cc1c46d2ab434e5f0d5efd8))

### Features

- Add get_token method to Api client
  ([`a1bc957`](https://github.com/rossumai/rossum-api/commit/a1bc957540f84ba2ff0be7540d509a84580c1cef))


## v0.3.0 (2022-10-17)

### Features

- Add request_json method to ElisAPIClient
  ([`6c2df87`](https://github.com/rossumai/rossum-api/commit/6c2df874934cc5bc2640aeee074cc57cd9cb4faa))


## v0.2.0 (2022-10-13)

### Features

- Implement retrying of failed requests
  ([`09ab473`](https://github.com/rossumai/rossum-api/commit/09ab47332fce0c9700107b47ca06d7a1712d653a))


## v0.1.3 (2022-10-12)

### Bug Fixes

- Change Annotation.confirmed_at type to str instead of datetime
  ([`40597bb`](https://github.com/rossumai/rossum-api/commit/40597bbc937277c04ebdd08d6422df9acfdf9dc7))


## v0.1.2 (2022-10-11)

### Bug Fixes

- Allow null Organization.trial_expires_at in the model
  ([`dd95716`](https://github.com/rossumai/rossum-api/commit/dd95716f0409c2416cc5637879acd0cdb9aa205f))


## v0.1.1 (2022-10-11)

### Bug Fixes

- Making dependency requirements more relaxed
  ([`80526da`](https://github.com/rossumai/rossum-api/commit/80526da75647be25c7fed581b7a51b337fc98a55))


## v0.1.0 (2022-10-06)

- Initial Release
