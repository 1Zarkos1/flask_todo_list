import pytest
from todo import TaskForm
from datetime import timedelta, datetime
from wtforms.validators import ValidationError

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
def test_form_validation_on_missing_value(app_inst, title, date_due, description):
    with app_inst.test_request_context(
        method="POST",
        data={"title": title, "date_due": date_due, "description": description},
    ):
        form = TaskForm()
        assert form.title.data == title
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
