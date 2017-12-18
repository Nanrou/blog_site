from flask import g
from flask_httpauth import HTTPBasicAuth

from . import api
from .errors import forbidden
from .unfllow import USERNAME, PASSWORD

auth = HTTPBasicAuth()


@api.before_request
@auth.login_required
def before_request():
    pass


@auth.verify_password
def verify_password(username, password):
    if username == USERNAME and password == PASSWORD:
        return True
    else:
        return False
