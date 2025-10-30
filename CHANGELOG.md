# CHANGELOG

<!-- version list -->

## v3.3.0 (2025-10-27)

### Features

- Add training_queues field for Engine
  ([`6099877`](https://github.com/rossumai/rossum-sdk/commit/60998778b4859bc08d5a91f170aaa88cfb0da20d))

### Chores

- Upgrade pytest-httpx
  ([`59326f1`](https://github.com/rossumai/rossum-sdk/commit/59326f1fc6dd4fb1ee725537f8d600a80f191896))

- Replace python <=3.9 support with python 3.13
  ([`d3dc4bf`](https://github.com/rossumai/rossum-sdk/commit/d3dc4bfde7c3e967edde314dff36d0bcf51ce329))

- Publish package automatically to pypi upon release
  ([`5fd3b80`](https://github.com/rossumai/rossum-sdk/commit/5fd3b800994376f034ddb22574e031a3615a9fa9))


## v3.2.0 (2025-09-16)

### Features

- Add authenticate method to Rossum API client
  ([`9bc0d86`](https://github.com/rossumai/rossum-sdk/commit/9bc0d86b035967205f7b847f90b2f13a7907d425))


## v3.1.3 (2025-09-10)

### Bug Fixes

- Fix sideload in sync client
  ([`e140569`](https://github.com/rossumai/rossum-sdk/commit/e140569066e54578a61aa76fe99d4c10018a2166))


## v3.1.2 (2025-09-08)

### Bug Fixes

- Switch from token header to Bearer auth and update tests (+ Sync client)
  ([`20d715b`](https://github.com/rossumai/rossum-sdk/commit/20d715b0bb9eb326bfb39508fd25465ce727f003))

- Switch from token header to Bearer auth and update tests
  ([`45ed114`](https://github.com/rossumai/rossum-sdk/commit/45ed114a0ebba1f9a7c9912deef1181f410b2cd9))


## v3.1.1 (2025-06-27)

### Bug Fixes

- Use venv pytest for the test command
  ([`fb24918`](https://github.com/rossumai/rossum-sdk/commit/fb24918063ef949d3786acc0e21dd7387ba4d7e2))


## v3.1.0 (2025-06-06)

### Features

- Add einvoice document relation type
  ([`2396694`](https://github.com/rossumai/rossum-sdk/commit/2396694ec085d11aae89489864c8bc1aec5c91ea))


## v3.0.0 (2025-05-28)

### Features

- Add email resource
  ([`4b2509b`](https://github.com/rossumai/rossum-sdk/commit/4b2509ba10256b3ad1a28e72e675f80457e5f6d3))

- Add email_imported task type
  ([`a1db151`](https://github.com/rossumai/rossum-sdk/commit/a1db15126262f580b04e37c52aa8b5b6be03b685))

### Bug Fixes

- Make Task.content optional
  ([`48d1e4d`](https://github.com/rossumai/rossum-sdk/commit/48d1e4dcd20a6be1d69b36424ede3c6cc86f90a7))

### Breaking Changes

- Adding email resource and task type can break existing setups.


## v2.1.0 (2025-05-28)

### Features

- Add missing annotation fields
  ([`71c2e2d`](https://github.com/rossumai/rossum-sdk/commit/71c2e2d732da01a5ff1b1d3bc6542f763f008d7e))


## v2.0.1 (2025-04-28)

### Bug Fixes

- Move exceptions module to rossum_api package
  ([`548215a`](https://github.com/rossumai/rossum-sdk/commit/548215a4bf04934ba0b80eb8078da314202d92d3))

It's not importable like this if user only installs the rossum-api package.


## v2.0.0 (2025-04-24)

### Features

- Add document relation resource
  ([`230bb1c`](https://github.com/rossumai/rossum-sdk/commit/230bb1c8be1f25be9a0f844a831ce2600bedcfa7))

BREAKING CHANGE: Adding to Generic class can break existing setups.

### Breaking Changes

- Adding to Generic class can break existing setups.


## v1.0.1 (2025-04-04)

### Bug Fixes

- Fix bugs in internal sync client
  ([`5e57018`](https://github.com/rossumai/rossum-sdk/commit/5e57018b5f2a99b3f37cfe5045d2a2b538432471))

- Use helpers from domain logic in clients - Add retry parameters to the constructor of the internal
  sync client - Add retries to the authentication method - Fix wrong method name in the export
  method - Fix the _stream method - Add a max_pages parameter to the fetch_resources method - Raise
  correct exceptions from the _request method - Add tests for the internal sync client

### Refactoring

- Rename module with tests of internal async client
  ([`1334338`](https://github.com/rossumai/rossum-sdk/commit/1334338ab372d2e7313fcf12961cb442892007e0))

And extract ot conftest things that will be common for both internal clients.

- Use helpers from domain logic in clients
  ([`24e0657`](https://github.com/rossumai/rossum-sdk/commit/24e0657a131aa3629596b582e41dcca04580197f))


## v1.0.0 (2025-03-26)

### Features

- Implement sync client without event loop
  ([`3964632`](https://github.com/rossumai/rossum-sdk/commit/3964632e9fd112cef5bc8c8c001ef39398fff48f))

BREAKING CHANGE: Public interface changed.

### Breaking Changes

- Public interface changed.


## v0.24.0 (2025-03-21)

### Features

- Add response post-processor
  ([`a1ab75f`](https://github.com/rossumai/rossum-sdk/commit/a1ab75fe505af59ffb363b69439abc4596a156bb))

Useful e.g. for logging.


## v0.23.2 (2025-03-20)

### Bug Fixes

- Resolve problem with typing and custom deserializer
  ([`a9b95bd`](https://github.com/rossumai/rossum-sdk/commit/a9b95bd16bb2df227727cc30b52d3189ed97f0e9))

When user used a custom deserializer, the typing hints were wrong. This should fix it in a
  backwards-compatible manner.


## v0.23.1 (2025-01-23)

### Bug Fixes

- Rename retrieve_engine_queue_stats to retrieve_engine_queues
  ([`7583358`](https://github.com/rossumai/rossum-sdk/commit/7583358da05b37f822e60f9c7b440064d20fbe7c))

The new name better conveys the essence that we're retrieving only a list of queues associated with
  the given engine. The docstring pointing to official documentation was also corrected.


## v0.23.0 (2025-01-20)

### Features

- Add more information to APIClientError
  ([`53d0781`](https://github.com/rossumai/rossum-sdk/commit/53d07810ccad959a3d110f622c8c46316a374a01))

- Add support for filters in export helper methods
  ([`8a94d6f`](https://github.com/rossumai/rossum-sdk/commit/8a94d6fbba26ed9db1c59499577f93d53a252d36))


## v0.22.0 (2025-01-16)

### Bug Fixes

- Remove 'button' possibility for EngineField.type as it should not happen
  ([`da698b0`](https://github.com/rossumai/rossum-sdk/commit/da698b01ef2438ebe658dc7e6e67a5b48a60ec81))

- Use _iter_over_async instead of _run_coroutine and Iterator instead of list
  ([`9540929`](https://github.com/rossumai/rossum-sdk/commit/95409299c468e28a4d89e2a90646d9d2aa73a33e))

Fixing several implementation as well as typing errors introduced in one of the recent pull
  requests.

### Code Style

- Reformat method parameters - do not break lines if not necessary
  ([`31537af`](https://github.com/rossumai/rossum-sdk/commit/31537af555c87f2f3563135692e6530d384e42a3))

### Features

- Support retrieval of Queues associated with the given Engine
  ([`8aee3d4`](https://github.com/rossumai/rossum-sdk/commit/8aee3d43a52a8d18bbdb19746675050a7efa89b8))


## v0.21.0 (2025-01-14)

### Chores

- Correct resource name in sideloading test integration test
  ([`a419002`](https://github.com/rossumai/rossum-sdk/commit/a4190024be69ec2f61ab533abee23415598240ec))

### Features

- Add support for retrieving EngineFields
  ([`c976954`](https://github.com/rossumai/rossum-sdk/commit/c976954d35369ab3f03b40861093f5ff257ec5a4))

### Refactoring

- Extract sideloading logic into domain logic
  ([`080b7af`](https://github.com/rossumai/rossum-sdk/commit/080b7afbb2f1a7ec3651ee80a6561c9921c55aaf))

...and use inflect to convert resource names to singular.


## v0.20.1 (2024-12-11)

### Bug Fixes

- Prevent race condition over the asyncio event loop in ThreadPoolExecutor
  ([`6a4d922`](https://github.com/rossumai/rossum-sdk/commit/6a4d922f9ebe98aa82ab2395f4b62c749eb89c10))

### Chores

- Extract Resource into domain logic
  ([`99ec60c`](https://github.com/rossumai/rossum-sdk/commit/99ec60c1fa51dccc684b600b976608807b681e5b))

- Extract URL domain logic into a reusable module
  ([`826fcd5`](https://github.com/rossumai/rossum-sdk/commit/826fcd5e766bde55f6f4bfc991a22ce422cac7dd))


## v0.20.0 (2024-12-10)

### Bug Fixes

- Do not crash when running sync client in async context
  ([`0038e4a`](https://github.com/rossumai/rossum-sdk/commit/0038e4a3bfe2f2312a4dfb91f0a7988ba1c798ac))

The asyncio code is now executed in a ThreadPoolExecutor to avoid problems with multiple event
  loops.

### Chores

- Fix tests by pinning pytest-httpx
  ([`a0c0eeb`](https://github.com/rossumai/rossum-sdk/commit/a0c0eeb85334f9c3bd86e599ab01c26f5c3bf275))

0.22 is the last version that works with Python 3.8.

- Improve readability of assert in XML export test
  ([`4c88b7e`](https://github.com/rossumai/rossum-sdk/commit/4c88b7e4328f01035a5c9f64ab4b013cce82bb73))

### Features

- Retry also on request/HTTP errors during authentication
  ([`3bae7da`](https://github.com/rossumai/rossum-sdk/commit/3bae7dad7d045faad0caf1a038aaf6d0400cbe47))

When Elis API fails intermittently, we were not retrying which leads to unnecessary failures in
  production when the client is used.


## v0.19.0 (2024-09-25)

### Chores

- Fix naming in queues tests
  ([`2c51b64`](https://github.com/rossumai/rossum-sdk/commit/2c51b640124394cb86c85e23546d0dd591ecfdf9))

### Features

- Add cancel annotation method
  ([`a217b64`](https://github.com/rossumai/rossum-sdk/commit/a217b64dc4609bca144322a5fe93dff26b0ff752))

- Add new methods for hook object
  ([`232269f`](https://github.com/rossumai/rossum-sdk/commit/232269fe8582c4d553172f510265a0b8cbccfaff))

- Add retrieve document method
  ([`4edac76`](https://github.com/rossumai/rossum-sdk/commit/4edac76684b0ac9cb8146dafaa1f92214bfe02e1))


## v0.18.1 (2024-08-20)

### Bug Fixes

- Handle http:// urls for local development
  ([`715513d`](https://github.com/rossumai/rossum-sdk/commit/715513d8144c8ede02d7288788fd73ca5722a2e3))


## v0.18.0 (2024-08-15)

### Features

- Add basic support for EmailTemplate object
  ([`0dc2882`](https://github.com/rossumai/rossum-sdk/commit/0dc28825f9f76e4f8bd6f10742f23ebf10633025))


## v0.17.2 (2024-08-12)

### Bug Fixes

- Fix typing of filters kwargs in sync client
  ([`7ae75e1`](https://github.com/rossumai/rossum-sdk/commit/7ae75e1bb335f0c52656982315eb4d39f5b84a62))


## v0.17.1 (2024-08-09)

### Bug Fixes

- Use Iterator instead of Iterable types
  ([`77edb52`](https://github.com/rossumai/rossum-sdk/commit/77edb529e4b69c74695bc16516cfe27ba9094c01))

Iterator is a better type for the method return value, since it correctly type checks the use of
  `next()`. Iterable interface doesn't.


## v0.17.0 (2024-08-08)

### Features

- Add delete method to Rossum API client
  ([`2c7db0a`](https://github.com/rossumai/rossum-sdk/commit/2c7db0a1b27ac82db7f4ec831caadf0c1f6c28f5))

- Support user-defined deserialization of sideloaded data
  ([`b12ad23`](https://github.com/rossumai/rossum-sdk/commit/b12ad239b21b3c5cb3f89e8f8f2a652c4cbb7ad3))

- Support XML document export with sideloads
  ([`ac02c11`](https://github.com/rossumai/rossum-sdk/commit/ac02c1141cc73c92cbbc68a1b40ad94a1c62ad1f))

### Bug Fixes

- Fix typing of resource delete methods
  ([`e55aaad`](https://github.com/rossumai/rossum-sdk/commit/e55aaad63d52c7e21a73b3e10ac8c5e5c30b20e0))

### Testing

- Add test for the sideload mechanism
  ([`e84c7e8`](https://github.com/rossumai/rossum-sdk/commit/e84c7e8a5ea2ea2d91b2c96e5e5e8e8a6a6d12e6))


## v0.16.0 (2024-06-20)

### Features

- Add support for updating inbox
  ([`6b6f20a`](https://github.com/rossumai/rossum-sdk/commit/6b6f20a1c3ecdc3e8a3c0c5ae81a5e8a80ba123d))

### Bug Fixes

- Fix organization trial fields typing
  ([`b80720c`](https://github.com/rossumai/rossum-sdk/commit/b80720c94ac7f80ed6ac9b33e44c0fe0bb3b9d1f))


## v0.15.0 (2024-05-16)

### Features

- Add support for connector
  ([`da885c1`](https://github.com/rossumai/rossum-sdk/commit/da885c1a1a76a6b2a2a46a84a08e16a2cf45a1f2))

- Add support for inbox
  ([`90fb2ab`](https://github.com/rossumai/rossum-sdk/commit/90fb2ab8a79b3f5e58f9ac5dd4f41b70a6ed2b5b))

- Add username to user model
  ([`6a07d33`](https://github.com/rossumai/rossum-sdk/commit/6a07d33a3bb0bb7e30c623d6e5e0f7a5096a7ad5))


## v0.14.0 (2024-04-16)

### Features

- Add Group.parent
  ([`9b91b0e`](https://github.com/rossumai/rossum-sdk/commit/9b91b0e6a8b6cb9c9bf6ebfba72c1bce46b87eeb))

### Bug Fixes

- Include py.typed file for mypy support
  ([`5f8fb95`](https://github.com/rossumai/rossum-sdk/commit/5f8fb959b0ffb2b2c3a9b3f1ab7bfd92a53c1eb3))


## v0.13.0 (2024-04-04)

### Features

- Add more fields to Hook model
  ([`e5ff8e6`](https://github.com/rossumai/rossum-sdk/commit/e5ff8e66f6d24fd9b24b5b3c2c2d9c8e9a097cd7))

- Enable cancelling annotation that is in the to_review state
  ([`b2eb6d9`](https://github.com/rossumai/rossum-sdk/commit/b2eb6d95fafbc3cadb9ea0da8fad8a4374b58b2b))

### Bug Fixes

- Allow None for Hook.settings
  ([`ee7ba5a`](https://github.com/rossumai/rossum-sdk/commit/ee7ba5af0de6e7ac89c5dc0e2b1fb5a01ba3ba34))


## v0.12.1 (2024-02-22)

### Bug Fixes

- Allow all possible values for annotation status
  ([`dbbba35`](https://github.com/rossumai/rossum-sdk/commit/dbbba35ddeb2c18bdde83e8f8a924aefaf2efd1e))

Since it's an enum that can be extended on the server side, we shouldn't restrict its values.


## v0.12.0 (2024-02-13)

### Features

- Add export convenience methods to the client
  ([`be0d7ae`](https://github.com/rossumai/rossum-sdk/commit/be0d7ae2ff6e04b9b26e0e3c1c70c2e4c8aaa9d8))

- Add sideloading support
  ([`d55a98e`](https://github.com/rossumai/rossum-sdk/commit/d55a98e1b7e35eaf04cee3b1e28e60892d24d13e))

This enables users to include related data when retrieving objects from API.

### Bug Fixes

- Remove side-effects from tests with sideloads
  ([`c3f8130`](https://github.com/rossumai/rossum-sdk/commit/c3f8130561815f1a8f26d7f25a557e77f9e625b3))

dummy_annotation was modified by a side-effect and the expected values didn't need to add content
  which was confusing.

### Features

- Add convenience methods for annotation lifecycle
  ([`cf56272`](https://github.com/rossumai/rossum-sdk/commit/cf56272354634a5002030c977ac295b72a15a3aa))

### Refactoring

- Rename UserRole to Group for consistency with the API
  ([`ed8065a`](https://github.com/rossumai/rossum-sdk/commit/ed8065a5abda3a69e3f8347626e63d67ad5f4c5d))


## v0.10.0 (2023-11-02)

### Chores

- Streamline Makefile and improve README
  ([`0b1064f`](https://github.com/rossumai/rossum-sdk/commit/0b1064f74fd2a60ce3c5a5fc6cde6194a3413907))

### Features

- Support deserializing of API payloads to user-defined model classes
  ([`a1e1385`](https://github.com/rossumai/rossum-sdk/commit/a1e1385649d974637bec33bd920705d0cdb56f2f))

Users can provide a custom deserializer that allows customising which models should be returned by
  the client.

### Refactoring

- Use an enum instead of strings to identify API resources
  ([`acbf731`](https://github.com/rossumai/rossum-sdk/commit/acbf731d369b0adfd2da9268008ca458848a20b1))

This is not only cleaner but will be useful when implementing custom de-serializers.


## v0.9.1 (2023-10-11)

### Bug Fixes

- **api_client**: Limit in-flight requests
  ([`56244d0`](https://github.com/rossumai/rossum-sdk/commit/56244d07569ad075ecd4703c3794a344eb609acd))

Limit the maximum number of fetch_all page requests running at in parallel.


## v0.9.0 (2023-10-11)

### Features

- Export public interface in root package
  ([`f85fc58`](https://github.com/rossumai/rossum-sdk/commit/f85fc58f017b5108b46819af8cf592e34de3f3e5))


## v0.8.0 (2023-08-25)

### Features

- **api_client**: Allow passing json argument in `fetch_all` as request payload
  ([`e433f85`](https://github.com/rossumai/rossum-sdk/commit/e433f858bbca35c7cf3211a7dabbbea921ec431d))

- **elis_api_clients**: Add new `search_for_annotations` method
  ([`34b3f72`](https://github.com/rossumai/rossum-sdk/commit/34b3f7249c149d0fa2da6fa1a171b92f0a0a2ffa))


## v0.7.4 (2023-08-11)

### Features

- **models**: Add token_lifetime_s attribute to hook model
  ([`f75dcfd`](https://github.com/rossumai/rossum-sdk/commit/f75dcfd5d346edadef9e56532316b217d069fbbb))


## v0.7.3 (2023-08-07)

### Bug Fixes

- Make time_spent in Annotation optional
  ([`a2e5d70`](https://github.com/rossumai/rossum-sdk/commit/a2e5d70a777b2c2fb0fc77b78eb005311cd36853))


## v0.7.2 (2023-06-02)

### Bug Fixes

- Add await to asyncio.sleep
  ([`4a537ab`](https://github.com/rossumai/rossum-sdk/commit/4a537ab6641e7745383a45dba7dd77bc0d6eb28c))


## v0.7.1 (2023-05-05)

### Bug Fixes

- **models**: Allow Any in metadata dict values in Queue model
  ([`7abaa13`](https://github.com/rossumai/rossum-sdk/commit/7abaa135a5f5f30f6e001afa9d22258dc89fcbc1))

- **models**: Allow null workspace in Queue model
  ([`dea0027`](https://github.com/rossumai/rossum-sdk/commit/dea00275c23d8b121ad29c1e624e74431923a4b0))


## v0.7.0 (2023-05-04)

### Features

- **elis_api_client**: Add generic method for requests to paginated resources
  ([`6b290e8`](https://github.com/rossumai/rossum-sdk/commit/6b290e8cb340f7be81768b311678163a3bfc41a8))


## v0.6.0 (2023-04-28)

### Chores

- Run test workflow also on pull requests
  ([`0ca9b43`](https://github.com/rossumai/rossum-sdk/commit/0ca9b43a555fbf3e238867a538e1459581351a74))

### Features

- **api_client**: Allow to set max pages limit in filters
  ([`090114f`](https://github.com/rossumai/rossum-sdk/commit/090114fbaecc3d84706715e80f119e623882826a))


## v0.5.1 (2023-03-31)

### Bug Fixes

- Switch from TravisCI to Github Workflows
  ([`de09e69`](https://github.com/rossumai/rossum-sdk/commit/de09e698f20c587932d5ad050d68f96e043ad645))

### Chores

- Fix semantic release
  ([`f1e56a5`](https://github.com/rossumai/rossum-sdk/commit/f1e56a57ac9d0210b5e3258ae71d63950c5598d1))


## v0.5.0 (2023-03-06)

### Features

- **rossum_sdk/api_client**: Add `request` method to ElisApiClient
  ([`5d11c3e`](https://github.com/rossumai/rossum-sdk/commit/5d11c3e5e70e22f2875787b8ee960b8184ddb99d))


## v0.4.0 (2023-03-02)

### Bug Fixes

- Define `Document.creator` as optional ([#35](https://github.com/rossumai/rossum-sdk/pull/35),
  [`d797e99`](https://github.com/rossumai/rossum-sdk/commit/d797e99112416602487409aaa668327fd80663aa))

Co-authored-by: Ondrej Slama <ondrej.slama@rossum.ai>

- **models:hook**: Define some attributes (guide, read_more_url, extension_image_url) as optional
  ([`b16a456`](https://github.com/rossumai/rossum-sdk/commit/b16a456344b41908c16c32b4d5be70d31f3b07b3))

### Chores

- Add pre-commit hook for commit messages
  ([`e641469`](https://github.com/rossumai/rossum-sdk/commit/e6414696a7cd9405978c2afd0a3aa050ee7fc9e6))

- Do not run commitizen when there is no commit
  ([`4f534d5`](https://github.com/rossumai/rossum-sdk/commit/4f534d55f8b6dd1bd981c3fe8aa1c00c36af493e))

- Fix mypy installation in pre-commit by upgrading it
  ([`5d4b387`](https://github.com/rossumai/rossum-sdk/commit/5d4b3870570cd7fcd82e86c8835246e7733e29ed))

The old version installed a version of `types-ats` that caused a crash during pre-commit
  installation.

- Fix tests that started failing with pytest-httpx==0.21.2
  ([`da18d27`](https://github.com/rossumai/rossum-sdk/commit/da18d275eebc4f85af8a6c6f913f430e8e1b871c))

The library no longer ignores missing empty URL parameters when matching URLs.

- Run semrel only once
  ([`3b9392a`](https://github.com/rossumai/rossum-sdk/commit/3b9392ab7cbcbe049cc1c46d2ab434e5f0d5efd8))

### Features

- Add get_token method to Api client
  ([`a1bc957`](https://github.com/rossumai/rossum-sdk/commit/a1bc957540f84ba2ff0be7540d509a84580c1cef))


## v0.3.0 (2022-10-17)

### Features

- Add request_json method to ElisAPIClient
  ([`6c2df87`](https://github.com/rossumai/rossum-sdk/commit/6c2df874934cc5bc2640aeee074cc57cd9cb4faa))


## v0.2.0 (2022-10-13)

### Features

- Implement retrying of failed requests
  ([`09ab473`](https://github.com/rossumai/rossum-sdk/commit/09ab47332fce0c9700107b47ca06d7a1712d653a))

APIClient now accepts retry configuration where number of retries and backoff can be configured.


## v0.1.3 (2022-10-12)

### Bug Fixes

- Change Annotation.confirmed_at type to str instead of datetime
  ([`40597bb`](https://github.com/rossumai/rossum-sdk/commit/40597bbc937277c04ebdd08d6422df9acfdf9dc7))


## v0.1.2 (2022-10-11)

### Bug Fixes

- Allow null Organization.trial_expires_at in the model
  ([`dd95716`](https://github.com/rossumai/rossum-sdk/commit/dd95716f0409c2416cc5637879acd0cdb9aa205f))


## v0.1.1 (2022-10-11)

### Bug Fixes

- Making dependency requirements more relaxed
  ([`80526da`](https://github.com/rossumai/rossum-sdk/commit/80526da75647be25c7fed581b7a51b337fc98a55))


## v0.1.0 (2022-10-06)

### Chores

- Introduce semantic releasing
  ([`a485874`](https://github.com/rossumai/rossum-sdk/commit/a48587415bb6c197a3d50b91d80f08ace5e8548c))

### Documentation

- **readme**: Add helper page, add makefile
  ([`1c95bea`](https://github.com/rossumai/rossum-sdk/commit/1c95beac020fc3a88086fddb4979366cd6e3e06f))

### Features

- First github release by semantic releasing
  ([`7dd7780`](https://github.com/rossumai/rossum-sdk/commit/7dd77806b030994b00027a17de1895142d852e48))

### Testing

- **api_client**: Reauth correct exception handling
  ([`5c0d728`](https://github.com/rossumai/rossum-sdk/commit/5c0d728644fb6a8d1884ce236afdfe9b7ef76bb1))
