from datetime import timedelta, datetime

import pytest
from wtforms.validators import ValidationError
from flask_wtf.csrf import generate_csrf
from flask_login import current_user

from todo import TaskForm, RegistrationForm, LoginForm, User, db, Task

VALID_DUE_DATE = datetime.now() + timedelta(days=1)


def test_index_page(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Create new task" in resp.data.decode("utf-8")


def test_task_addition(client):
    resp = client.post(
        "/",
        data={
            "title": "Test title",
            "description": "Test description",
            "date_due": VALID_DUE_DATE.strftime("%Y-%m-%dT%H:%M"),
        },
        follow_redirects=True,
    )
    assert len(Task.query.all()) == 1
    assert b"Test title" in resp.data
    assert b"Test description" in resp.data


@pytest.mark.parametrize(
    "title,date_due,description",
    [
        ("", VALID_DUE_DATE, "test descrition"),
        ("test title", "", "test description"),
        ("test title", VALID_DUE_DATE, ""),
        ("test title", "random", "test"),
    ],
)
def test_task_form_validation_on_missing_value(app_inst, title, date_due, description):
    with app_inst.test_request_context(
        method="POST",
        data={"title": title, "date_due": date_due, "description": description},
    ):
        form = TaskForm()
        assert form.validate_on_submit() == False


@pytest.mark.parametrize(
    "date_due",
    [VALID_DUE_DATE, 2222, VALID_DUE_DATE.strftime("%Y-%m-%d"), "random string"],
)
def test_incorrect_date_due_format(client, date_due):
    resp = client.post(
        "/",
        data={
            "title": "Test title",
            "description": "Test description",
            "date_due": date_due,
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"Not a valid datetime value" in resp.data


def test_correct_registration_form(app_inst):
    with app_inst.test_request_context():
        form = RegistrationForm(
            email="example@mail.com", password="test", pass_repeat="test"
        )
        assert form.validate() == True


@pytest.mark.parametrize(
    "email,password,error",
    [
        ("example@mail.com", "fizz", "pass_repeat"),
        ("something_mail.com", "test", "email"),
    ],
)
def test_incorrect_data_in_registration_form(app_inst, email, password, error):
    with app_inst.test_request_context():
        form = RegistrationForm(email=email, password="test", pass_repeat=password)
        assert form.validate() == False
        assert len(form.errors) == 1
        assert error in form.errors


def test_user_already_exists_in_registration_form(app_inst):
    db.session.add(User(email="example@mail.com", password="test"))
    db.session.commit()
    with app_inst.test_request_context():
        form = RegistrationForm(
            email="example@mail.com", password="test", pass_repeat="test"
        )
        assert form.validate() == False
        assert len(form.errors) == 1
        assert "User with this email already exist" in form.errors["email"]


def test_user_registration(app_inst, client):
    resp = client.post(
        "/register/",
        data={
            "email": "test@mail.com",
            "password": "test",
            "pass_repeat": "test",
        },
        follow_redirects=True,
    )
    users = User.query.all()
    user = users[0]
    assert len(users) == 1
    assert user.email == "test@mail.com"


def test_user_login(app_inst, client):
    with app_inst.test_request_context():
        user = User(email="test@mail.com", password="pass")
    db.session.add(user)
    db.session.commit()
    resp = client.post(
        "/",
        data={
            "email": "test@mail.com",
            "password": "pass",
        },
        follow_redirects=True,
    )
    assert b"test@mail.com" in resp.data
    assert b"Log Out" in resp.data
