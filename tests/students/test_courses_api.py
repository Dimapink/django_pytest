import pytest
from students.models import Course, Student
from tests.conftest import course_factory


@pytest.mark.django_db
def test_api_retrieve_course(api_client, course_factory):
    course = course_factory(_quantity=1)
    target_course_id = Course.objects.get(name=course[0].name).pk
    response = api_client.get(f"/api/v1/courses/{target_course_id}/")
    course_students = Course.objects.get(id=1).students.count()
    # status
    assert response.status_code == 200, f"{response.status_code=}"
    response_data = response.json()
    # id is ident
    assert response_data.get("id") == 1
    # name is ident
    assert response_data.get("name") == course[0].name, f'{response_data.get("name")=}\n {course[0].name=}'
    # len of related students is ident
    assert len(response_data.get("students")) == course_students, (f'{response_data.get("students")=}\n'
                                                                   f'{course[0].students=}')

@pytest.mark.django_db
def test_api_get_courses_list(api_client, course_factory):
    courses = course_factory(_quantity=5)
    response = api_client.get("/api/v1/courses/")
    data = response.json()
    # response is 200
    assert response.status_code == 200
    # len courses is ident
    assert len(data) == len(courses)
    for gotten_course, target_course in zip(data, courses):
        gotten_students = gotten_course.get("students")
        target_students = Course.objects.get(id=gotten_course.get("id")).students.count()
        # course names is ident
        assert gotten_course.get("name") == target_course.name
        # course students is ident
        assert len(gotten_students) == target_students

@pytest.mark.django_db
def test_api_filter_course_by_id(api_client, course_factory):
    courses = course_factory(_quantity=5)
    target_course = courses[0]
    target_course_id = Course.objects.get(name=target_course.name).pk
    response = api_client.get(f"/api/v1/courses/?id={target_course_id}")
    response_data = response.json()

    assert response.status_code == 200, f"{response.status_code=}"
    assert response_data[0].get("id") == target_course_id
    assert response_data[0].get("name") == target_course.name

@pytest.mark.django_db
def test_api_filter_course_by_name(api_client, course_factory):
    courses = course_factory(_quantity=5)
    target_course = courses[2]
    response = api_client.get(f"/api/v1/courses/?name={target_course.name}")
    response_data = response.json()

    assert response.status_code == 200, f"{response.status_code=}"
    assert response_data[0].get("id") == target_course.id
    assert response_data[0].get("name") == target_course.name


@pytest.mark.django_db
def test_api_create_course(api_client):
    payload = {'name': "test_create_course", "students":[]}
    response = api_client.post("/api/v1/courses/", data=payload)
    response_data = response.json()

    assert response.status_code == 201
    assert response_data.get("name") == payload.get("name")
    assert response_data.get("students") == payload.get("students")

@pytest.mark.django_db
def test_api_update_course_name(api_client, course_factory):
    course = course_factory(_quantity=1)
    target_course = Course.objects.filter(name=course[0].name)
    target_course_id = Course.objects.get(name=target_course[0].name).pk
    target_course_students = [x.get('students') for x in target_course.values("students")]
    payload = {'name': "updated_name", "students": target_course_students}
    response = api_client.patch(f"/api/v1/courses/{target_course_id}/", data=payload)
    assert response.status_code == 200
    response_data = response.json()

    # id have not changed
    assert response_data.get("id") == target_course_id
    # name has been changed
    assert response_data.get("name") == "updated_name"
    # students have not changed
    assert response_data.get("students") == target_course_students


@pytest.mark.django_db
def test_api_update_course_students(api_client, course_factory):
    course = course_factory(_quantity=1)
    target_course = Course.objects.filter(name=course[0].name)
    target_course_id = Course.objects.get(name=target_course[0].name).pk
    target_course_students = [x.get('students') for x in target_course.values("students")]
    students_for_payload = target_course_students[:-1]
    # берем срез списка имеющихся студентов кроме последнего
    payload = {'name': course[0].name, "students": students_for_payload}
    response = api_client.patch(f"/api/v1/courses/{target_course_id}/", data=payload)
    assert response.status_code == 200
    response_data = response.json()

    # id have not been changed
    assert response_data.get("id") == target_course_id
    # name has not been changed
    assert response_data.get("name") == course[0].name
    # students have been changed
    assert response_data.get("students") == students_for_payload

@pytest.mark.django_db
def test_api_delete_course(api_client, course_factory):
    course = course_factory(_quantity=1)
    target_course = Course.objects.filter(name=course[0].name)
    target_course_id = Course.objects.get(name=target_course[0].name).pk
    target_course_students = [x.get('students') for x in target_course.values("students")]
    response = api_client.delete(f"/api/v1/courses/{target_course_id}/")
    assert response.status_code == 204

    # курс невозможно повторно получить по id
    response_after_delete = api_client.get("/api/v1/courses/1/")
    assert response_after_delete.status_code == 404

    # студенты после удаления курса не удаляются
    current_students = Student.objects.all()
    students_after_delete = [x.get('id') for x in current_students.values("id")]
    assert students_after_delete == target_course_students
