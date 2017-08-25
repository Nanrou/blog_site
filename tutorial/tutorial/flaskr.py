import os

from flask import Flask, request, session, g, redirect,url_for, \
    abort, render_template, flash
from playhouse.flask_utils import FlaskDB

from .models import database, Entries

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'blog.db'),
    SECRET_KEY='luluamao',
    USERNAME='admin',
    PASSWORD='default',
))

app.config.from_envvar('FLASKR_SETTINGS', silent=True)

db_wrapper = FlaskDB(app, database)

