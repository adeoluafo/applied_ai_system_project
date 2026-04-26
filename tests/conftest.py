import pytest
from datetime import datetime
from pawpal_system import PetOwner, Pet, Task, Schedule


@pytest.fixture
def owner():
    return PetOwner("Alice", 480, "None")


@pytest.fixture
def dog():
    return Pet("Buddy", "Dog", 3, "None")


@pytest.fixture
def cat():
    return Pet("Whiskers", "Cat", 2, "None")


@pytest.fixture
def walk_task():
    return Task("Walk", 30, "high", "exercise", "daily", "08:00", "pending", "Buddy", datetime.now())


@pytest.fixture
def feed_task():
    return Task("Feed", 15, "medium", "feeding", "daily", "12:00", "pending", "Buddy", datetime.now())
