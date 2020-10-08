import pytest

from todo import app, db


@pytest.fixture
def client(app_inst):
    # app_inst.config["WTF_CSRF_ENABLED"] = True
    with app_inst.test_client() as client:
        yield client


@pytest.fixture
def app_inst():
    app.config.from_object("config.TestConfig")
    db.create_all()
    yield app
    db.drop_all()