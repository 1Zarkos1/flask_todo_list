class DevConfig:
    SECRET_KEY = "anotherkey"
    TESTING = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///tasks.db"
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig:
    SECRET_KEY = "somekey"
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"
