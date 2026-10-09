"""Model factories for domain tests."""

from __future__ import annotations

import uuid

import factory
from apps.activity.models import Activity
from apps.catalog.models import Category, File
from apps.catalog.models_metadata import FileMetadata
from apps.duplicates.models import DuplicateGroup, DuplicateMember
from apps.folders.models import Folder
from apps.jobs.models import Job
from apps.rules.models import OrganizationRule
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")


class FolderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Folder

    user = factory.SubFactory(UserFactory)
    path = factory.Sequence(lambda n: f"/data/folder_{n}")
    name = factory.Sequence(lambda n: f"folder_{n}")
    is_active = True
    is_watched = False
    recursive = True
    follow_symlinks = False


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    slug = factory.Sequence(lambda n: f"category_{n}")
    name = factory.Sequence(lambda n: f"Category {n}")
    is_system = False


class FileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = File

    folder = factory.SubFactory(FolderFactory)
    relative_path = factory.Sequence(lambda n: f"file_{n}.txt")
    canonical_path = factory.Sequence(lambda n: f"/data/file_{n}.txt")
    name = factory.Sequence(lambda n: f"file_{n}.txt")
    extension = "txt"
    size_bytes = 1024
    hash_stage = "none"


class FileMetadataFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FileMetadata

    file = factory.SubFactory(FileFactory)
    data = {"source": "factory"}


class DuplicateGroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DuplicateGroup

    size_bytes = 2048
    sha256 = factory.LazyFunction(lambda: uuid.uuid4().hex)
    member_count = 2
    reclaimable_bytes = 2048


class DuplicateMemberFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DuplicateMember

    group = factory.SubFactory(DuplicateGroupFactory)
    file = factory.SubFactory(FileFactory)
    is_keeper = False


class OrganizationRuleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrganizationRule

    user = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: f"rule_{n}")
    priority = 0
    is_active = True
    conditions = {}
    actions = {}


class JobFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Job

    user = factory.SubFactory(UserFactory)
    job_type = "scan"
    status = "pending"
    progress_percent = 0


class ActivityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Activity

    user = factory.SubFactory(UserFactory)
    event_type = "test_event"
    description = "test"
