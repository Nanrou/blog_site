import os
import time
from datetime import datetime

from flask_script import Manager, Shell
from playhouse.migrate import SqliteMigrator, migrate

from app import create_app, db_wrapper
from app.models import User, Post, Category


app = create_app(os.environ.get('FLASK_CONFIG') or 'default')
manager = Manager(app)


def make_shell_context():
    return dict(app=app, User=User, Post=Post, Category=Category)

manager.add_command('shell', Shell(make_context=make_shell_context))


@manager.command
def create_tables():
    db_wrapper.database.connect()
    db_wrapper.database.drop_tables([User, Post, Category], safe=True)
    db_wrapper.database.create_tables([User, Post, Category], safe=True)
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
def create_all():
    create_tables()
    filenames = []
    create_times = []
    titles = []
    bodys = []

    with open('./post/nnote.txt', 'r', encoding='utf-8') as rf:
        for line in rf.readlines():
            if line.strip():
                filename, create_time = line.split(',')
                filenames.append(filename.strip())
                create_times.append(create_time.strip())

    for filename in filenames:
        with open('./post/' + filename + '.md', 'r', encoding='utf-8') as f:
            title = f.readline().replace('#', '').strip()
            body = ''.join(f.readlines())
            titles.append(title)
            bodys.append(body)
    row_data = []
    for title, body, timestamp in zip(titles, bodys, create_times):
        row_data.append({'title': title, 'body': body, 'timestamp': timestamp})
        pp = Post.create(**{'title': title, 'body': body, 'timestamp': timestamp})
        pp.save()
    # Post.insert_many(row_data).execute()


if __name__ == '__main__':
    manager.run()
