import factory
from faker import Faker

from rossum_ng.models.annotation import Annotation
from rossum_ng.models.automation_blocker import AutomationBlocker, AutomationBlockerContent
from rossum_ng.models.document import Document
from rossum_ng.models.user import User

API_URL = "https://elis.rossum.ai/api/v1"


class DocumentFactory(factory.Factory):
    class Meta:
        model = Document

    class Params:
        base_url = API_URL

    id = factory.Faker("pyint")  # noqa: A003
    url = factory.LazyAttribute(lambda s: f"{s.base_url}/documents/{s.id}")
    s3_name = "7731c4d28b3bf6ae5e29f933798b1393"
    mime_type = "application/pdf"
    created_at = "2022-07-12T08:16:41.731996Z"
    arrived_at = "2022-07-12T08:16:41.731996Z"
    original_file_name = "test_lacte1.pdf"

    creator = factory.LazyAttribute(lambda s: f"{s.base_url}/users/{s.id}")
    content = factory.LazyAttribute(lambda s: f"{s.url}/content")
    annotations = factory.LazyAttribute(lambda s: [f"{s.base_url}/annotations/{Faker().pyint()}"])


class UserFactory(factory.Factory):
    class Meta:
        model = User

    class Params:
        base_url = API_URL

    id = factory.Faker("pyint")  # noqa: A003
    url = factory.LazyAttribute(lambda s: f"{s.base_url}/users/{s.id}")
    first_name = Faker().first_name()
    last_name = Faker().last_name()
    username = "test@user.com"
    email = "test@user.com"
    groups = factory.LazyAttribute(
        lambda s: [f"{s.base_url}/groups/{Faker().pyint(min_value=1, max_value=6)}"]
    )
    organization = factory.LazyAttribute(lambda s: f"{s.base_url}/organizations/{Faker().pyint()}")
    last_login = "2022-07-12T08:16:41.731996Z"
    date_joined = "2022-07-12T08:16:41.731996Z"


class AutomationBlockerContentFactory(factory.Factory):
    class Meta:
        model = AutomationBlockerContent

    type = "automation_disabled"
    level = "annotation"


class AutomationBlockerFactory(factory.Factory):
    class Meta:
        model = AutomationBlocker

    class Params:
        base_url = API_URL

    id = factory.Faker("pyint")  # noqa: A003
    url = factory.LazyAttribute(lambda s: f"{s.base_url}/automation_blockers/{s.id}")
    annotation = factory.LazyAttribute(lambda s: f"{s.base_url}/annotation/{Faker().pyint()}")

    content = factory.LazyAttribute(lambda _: [AutomationBlockerContentFactory()])


class AnnotationFactory(factory.Factory):
    class Meta:
        model = Annotation

    class Params:
        base_url = API_URL

        sideload = factory.Trait(
            modifier=UserFactory(),
            document=DocumentFactory(),
            automation_blocker=AutomationBlockerFactory(),
        )

    id = factory.Faker("pyint")  # noqa: A003
    document = factory.LazyAttribute(lambda s: f"{s.base_url}/documents/{Faker().pyint()}")
    queue = factory.LazyAttribute(lambda s: f"{s.base_url}/queues/{Faker().pyint()}")
    schema = factory.LazyAttribute(lambda s: f"{s.base_url}/schemas/{Faker().pyint()}")
    creator = factory.LazyAttribute(lambda s: f"{s.base_url}/users/{Faker().pyint()}")
    organization = factory.LazyAttribute(lambda s: f"{s.base_url}/organizations/{Faker().pyint()}")
    pages = factory.LazyAttribute(lambda s: [f"{s.base_url}/pages/{Faker().pyint()}"])

    # datetime more than 3 days old but not longer than 30 days
    created_at = "2022-07-12T08:16:41.731996Z"

    url = factory.LazyAttribute(lambda s: f"{s.base_url}/annotations/{s.id}")
    content = factory.LazyAttribute(lambda s: f"{s.url}/content")

    email = factory.LazyAttribute(lambda s: f"{s.base_url}/email/{Faker().pyint()}")
    email_thread = factory.LazyAttribute(lambda s: f"{s.base_url}/email_thread/{Faker().pyint()}")
    status = "to_review"
    rir_poll_id = "54f6b9ecfa751789f71ddf12"


# example
a = AnnotationFactory(sideload=True)
print(a)

import json

print(json.loads(a.json()))
