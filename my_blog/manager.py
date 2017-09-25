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
    post_cate = []

    cates = ['Django', '日常踩坑', '读书笔记', 'LeetCode', 'python', '一些翻译', 'linux']
    cate_dict = dict((k, v) for k, v in zip(cates, range(1, len(cates) + 1)))
    for c in cates:
        cc = Category(category=c)
        cc.save()

    with open('./post/nnnote.txt', 'r', encoding='utf-8') as rf:
        for line in rf.readlines():
            if line.strip():
                filename, create_time, cate = map(lambda s: s.strip(), line.split(','))
                filenames.append(filename)
                create_times.append(create_time)
                post_cate.append(cate_dict[cate])

    for filename in filenames:
        with open('./post/' + filename + '.md', 'r', encoding='utf-8') as f:
            title = f.readline().replace('#', '').strip()
            body = ''.join(f.readlines())
            titles.append(title)
            bodys.append(body)

    row_data = []
    for title, body, timestamp, cate in zip(titles, bodys, create_times, post_cate):
        row_data.append({'title': title, 'body': body, 'timestamp': timestamp})
        pp = Post.create(**{'title': title, 'body': body, 'timestamp': timestamp, 'category': cate})
        pp.save()
    # Post.insert_many(row_data).execute()  # 这个不调用__init__


if __name__ == '__main__':
    manager.run()
