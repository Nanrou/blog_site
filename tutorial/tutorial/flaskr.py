import os

from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash, current_app
from playhouse.flask_utils import FlaskDB, object_list

# from models import database, Entries
from peewee import *


app = Flask(__name__)
app.config.update(dict(
    DATABASE='sqliteext:///%s' % os.path.join(app.root_path, 'app.db'),
    SECRET_KEY='luluamao',
    USERNAME='admin',
    PASSWORD='default',
))
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

flask_db = FlaskDB(app)
database = flask_db.database


class Entries(flask_db.Model):
    title = CharField()
    text = TextField()


# def get_db():
#     if not hasattr(g, 'sqlite_db'):
#         g.sqlite_db = db_wrapper.connect_db()
#     return g.sqlite_db
#
#
# @app.teardown_appcontext
# def close_db(error):
#     if hasattr(g, 'sqlite_db'):
#         g.sqlite_db.close_db()


@app.route('/')
def show_entries():
    entries = (Entries.select().order_by(Entries.id.desc()))
    #return object_list(
    #   'show_entries.html',
    #    query=entries,
    #    context_variable='entries',
    #)
    return render_template('show_entries.html', entries=entries)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    with database.transaction():
        Entries.create(
            title=request.form['title'],
            text=request.form['text']
        )
    return redirect(url_for('show_entries'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config.get('USERNAME', 'admin'):
            error = 'Invalid username'
        elif request.form['password'] != current_app.config.get('PASSWORD', 'default'):
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
    database.create_tables([Entries], safe=True)
    app.run(debug=True)
