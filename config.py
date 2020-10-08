class DevConfig:
    SECRET_KEY = "sladjfaoi4j30348ru"
    TESTING = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///tasks.db"
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig:
    SECRET_KEY = "somekey"
    WTF_CSRF_ENABLED = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"
