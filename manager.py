import os
import time
from datetime import datetime

from flask_script import Manager, Shell
from playhouse.migrate import SqliteMigrator, migrate

from app import create_app, db_wrapper
from app.models import User, Post, Category, Comment


app = create_app(os.environ.get('FLASK_CONFIG') or 'default')
manager = Manager(app)


def make_shell_context():
    return dict(app=app, User=User, Post=Post, Category=Category, Comment=Comment)


manager.add_command('shell', Shell(make_context=make_shell_context))


@manager.command
def create_tables():
    db_wrapper.database.connect()
    db_wrapper.database.drop_tables([User, Post, Category, Comment], safe=True)
    db_wrapper.database.create_tables([User, Post, Category, Comment], safe=True)
    db_wrapper.database.close()


@manager.command
def drop_tables():
    db_wrapper.database.connect()
    db_wrapper.database.drop_tables([User, Post, Comment], safe=True)
    db_wrapper.database.close()


@manager.command
def update_tables():
    migrator = SqliteMigrator(db_wrapper.database)
    migrate(
        migrator.drop_not_null('posts', 'body_html'),
    )


def create_table_shortcut(*args):
    db_wrapper.database.connect()
    db_wrapper.database.drop_tables([*args], safe=True)
    db_wrapper.database.create_tables([*args], safe=True)
    db_wrapper.database.close()


@manager.command
def create_user():
    create_table_shortcut(User)
    row_data = []
    names = ['lulu', 'amao', 'john']
    for n in names:
        row_data.append({'nickname': n, 'email': '{}@cc.com'.format(n)})

    User.insert_many(row_data).execute()  # 这个不调用__init__


@manager.command
def create_comment():
    create_table_shortcut(Comment)
    Comment.create(content='lulu say something', author_id=1, post_id=52, timestamp=datetime.now())
    time.sleep(0.5)
    Comment.create(content='amao say something to lulu', author_id=2, post_id=52, timestamp=datetime.now(), quote_comment=1)
    time.sleep(0.5)
    Comment.create(content='amao say other thing to lulu', author_id=2, post_id=52, timestamp=datetime.now(), quote_comment=1)
    time.sleep(0.5)
    Comment.create(content='lulu say something back to amao', author_id=1, post_id=52, timestamp=datetime.now(), quote_comment=3)
    time.sleep(0.5)
    Comment.create(content='john say something to amao', author_id=3, post_id=52, timestamp=datetime.now(), quote_comment=2)
    time.sleep(0.5)
    Comment.create(content='john say something', author_id=3, post_id=52, timestamp=datetime.now())


@manager.command
def create_all():
    create_tables()

    filenames = []
    create_times = []
    titles = []
    bodys = []
    post_cate = []

    cate = ['Django', '日常踩坑', '读书笔记', 'LeetCode', 'python', '一些翻译', 'linux']
    cate_for_short = ['Django', 'daily', 'booknote', 'leetcode', 'python', 'translation', 'linux']
    for _c, _s in zip(cate, cate_for_short):
        cc = Category(category=_c, cate=_s)
        cc.save()

    cate_dict = dict((k, v) for k, v in zip(cate, range(1, len(cate) + 1)))  # 为文章匹配上分类的序号
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

    Category.count_posts()


if __name__ == '__main__':
    manager.run()
