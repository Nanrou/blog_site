import os
import time
from datetime import datetime

from flask_script import Manager, Shell
from playhouse.migrate import SqliteMigrator, migrate

from app import create_app, db_wrapper
from app.models import User, Post


app = create_app(os.environ.get('FLASK_CONFIG') or 'default')
manager = Manager(app)


def make_shell_context():
    return dict(app=app, User=User, Post=Post)

manager.add_command('shell', Shell(make_context=make_shell_context))


@manager.command
def create_tables():
    db_wrapper.database.connect()
    db_wrapper.database.create_tables([User, Post])
    db_wrapper.database.close()


@manager.command
def drop_tables():
    db_wrapper.database.connect()
    db_wrapper.database.drop_tables([User, Post], safe=True)
    db_wrapper.database.close()


@manager.command
def update_tables():
    migrator = SqliteMigrator(db_wrapper.database)
    migrate(
        migrator.drop_not_null('posts', 'body_html'),
    )


@manager.command
def create_one():
    pp = Post.delete().where(Post.id == 3)
    pp.execute()
    with open('the elements of computing systems 的读书笔记1.md', 'r', encoding='utf-8') as f:
        title = f.readline().replace('#', '').strip()
        body = ''.join(f.readlines())

    p = Post(title=title, body=body, )
    p.save()


if __name__ == '__main__':
    manager.run()
