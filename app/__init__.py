import logging

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_mail import Mail
from flask_login import LoginManager
from flask_debugtoolbar import DebugToolbarExtension
from flask_pagedown import PageDown
from playhouse.flask_utils import FlaskDB
from flask_caching import Cache

from config import CONFIG

# logger = logging.getLogger('peewee')
# logger.setLevel(logging.DEBUG)
# logger.addHandler(logging.StreamHandler())

bootstrap = Bootstrap()
moment = Moment()
db_wrapper = FlaskDB()
mail = Mail()
debugToolBar = DebugToolbarExtension()
pagedown = PageDown()
cache = Cache()

login_manager = LoginManager()
login_manager.login_message = '麻烦请先登陆'
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(CONFIG[config_name])
    CONFIG[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db_wrapper.init_app(app)
    login_manager.init_app(app)
    debugToolBar.init_app(app)
    pagedown.init_app(app)
    cache.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app
