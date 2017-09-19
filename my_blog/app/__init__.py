from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_mail import Mail
from flask_login import LoginManager
from flask_debugtoolbar import DebugToolbarExtension
from flask_pagedown import PageDown
from playhouse.flask_utils import FlaskDB

from config import CONFIG

bootstrap = Bootstrap()
moment = Moment()
db_wrapper = FlaskDB()
mail = Mail()
debugToolBar = DebugToolbarExtension()
pagedown = PageDown()

login_manager = LoginManager()
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

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
