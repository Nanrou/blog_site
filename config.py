import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'so hard to guess'
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = 'Admin Nan <13532227149@163.com>'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN') or FLASKY_MAIL_SENDER

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 25
    MAIL_USE_TLS = True
    MAIL_USERNAME = '13532227149@163.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or '*'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URI') or 'sqlite:///' + os.path.join(BASEDIR, 'data.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = \
        os.environ.get('TEST_DATABASE_URI') or 'sqlite:///' + os.path.join(BASEDIR, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URI') or 'sqlite:///' + os.path.join(BASEDIR, 'pro.sqlite')


config = {
    'dev': DevelopmentConfig,
    'testing': TestingConfig,
    'pro': ProductionConfig,

    'default': DevelopmentConfig,
}

