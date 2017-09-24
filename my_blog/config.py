import os
import unfollow
BASEDIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = unfollow.SECRET_KEY
    FLASKY_MAIL_SENDER = unfollow.FLASKY_MAIL_SENDER
    MAIL_SERVER = unfollow.MAIL_SERVER
    MAIL_PORT = unfollow.MAIL_PORT
    MAIL_USERNAME = unfollow.MAIL_USERNAME
    MAIL_PASSWORD = unfollow.MAIL_PASSWORD
    MAIL_USE_TLS = True
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN') or FLASKY_MAIL_SENDER
    UPLOAD_FOLDER = os.path.join(BASEDIR, 'upload_folder')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False  # 取消打断重定向
    DATABASE = os.environ.get('DATABASE') or 'sqlite:///default.db'


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    DATABASE = os.environ.get('TEST_DATABASE') or 'sqlite:///:memory:'


class ProductionConfig(Config):
    pass


CONFIG = {
    'dev': DevelopmentConfig,
    'testing': TestingConfig,
    'pro': ProductionConfig,

    'default': DevelopmentConfig,
}
