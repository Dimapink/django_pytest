from random import randint

import pytest
from rest_framework.test import APIClient
from model_bakery import baker
from students.models import Student, Course

@pytest.fixture(scope="function")
def api_client():
    client = APIClient()
    yield client


@pytest.fixture
def course_factory():
    def factory(*args, **kwargs):
        students_set = baker.prepare(Student, _quantity=randint(1, 5))
        return baker.make(Course, *args, **kwargs, students=students_set, make_m2m=True)
    return factory
