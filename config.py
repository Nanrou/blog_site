import os
import unfollow
from peewee import SqliteDatabase

BASEDIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = unfollow.SECRET_KEY
    FLASKY_MAIL_SENDER = unfollow.FLASKY_MAIL_SENDER
    MAIL_SERVER = unfollow.MAIL_SERVER
    MAIL_PORT = unfollow.MAIL_PORT
    MAIL_USERNAME = unfollow.MAIL_USERNAME
    MAIL_PASSWORD = unfollow.MAIL_PASSWORD
    MAIL_USE_TLS = True
    FLASKY_MAIL_SUBJECT_PREFIX = "Nan's Home"
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN') or FLASKY_MAIL_SENDER
    UPLOAD_FOLDER = os.path.join(BASEDIR, 'upload_folder')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False  # 取消打断重定向
    DATABASE_URL = os.environ.get('DATABASE') or 'sqlite:///default.db'
    DATABASE = SqliteDatabase('./default.db', autocommit=False)
    CACHE_TYPE = 'simple'


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    DATABASE = os.environ.get('TEST_DATABASE') or 'sqlite:///:memory:'


class ProductionConfig(Config):
    DEBUG = False
    DATABASE_URL = os.environ.get('DATABASE') or 'sqlite:///default.db'
    DATABASE = SqliteDatabase('./default.db', autocommit=False)
    CACHE_TYPE = 'RedisCache'
    CACHE_REDIS_HOST = '172.17.0.3'
    CACHE_REDIS_DB = '3'


CONFIG = {
    'dev': DevelopmentConfig,
    'testing': TestingConfig,
    'pro': ProductionConfig,

    'default': DevelopmentConfig,
}
