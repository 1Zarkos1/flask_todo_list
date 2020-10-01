import pytest

from todo import app, db


@pytest.fixture
def client(app_inst):
    with app_inst.test_client() as client:
        app_inst.config["WTF_CSRF_ENABLED"] = False
        db.create_all()
        yield client
        db.drop_all()


@pytest.fixture
def app_inst():
    app.config.from_object("config.TestConfig")
    return app