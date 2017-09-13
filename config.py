import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'so hard to guess'
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = 'Admin Nan <13532227149@163.com>'
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 25
    MAIL_USE_TLS = True
    MAIL_USERNAME = '13532227149@163.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN') or FLASKY_MAIL_SENDER
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    FLASKY_DB_QUERY_TIMEOUT = 0.5

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URI') or 'sqlite:///' + os.path.join(BASEDIR, 'data.sqlite')
    # 官方文档中指出sqlite后面要跟4个斜杆的，但是源码中还是3个斜杆
    DEBUG_TB_INTERCEPT_REDIRECTS = False  # 取消打断重定向


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = \
        os.environ.get('TEST_DATABASE_URI') or 'sqlite:///' + os.path.join(BASEDIR, 'data-tests.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URI') or 'sqlite:///' + os.path.join(BASEDIR, 'pro.sqlite')


CONFIG = {
    'dev': DevelopmentConfig,
    'testing': TestingConfig,
    'pro': ProductionConfig,

    'default': DevelopmentConfig,
}

