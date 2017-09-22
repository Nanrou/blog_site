import os
from random import randint
from datetime import datetime
import re

from flask import url_for
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from peewee import CharField, IntegerField, DateTimeField, TextField, BooleanField, ForeignKeyField
from markdown import markdown
import bleach

from . import db_wrapper


class BaseModel(db_wrapper.Model):
    class Meta:
        database = db_wrapper.database


class User(UserMixin, BaseModel):
    username = CharField(max_length=32, index=True)
    password_hash = CharField(max_length=128)
    email = CharField(max_length=32, index=True)

    nickname = CharField(max_length=32)
    avatar_hash = CharField(max_length=128)

    member_since = DateTimeField(default=datetime.now())
    last_seen = DateTimeField(default=datetime.now())

    class Meta:
        db_table = 'users'

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


class Category(BaseModel):
    category = CharField(max_length=32, index=True)
    # count = IntegerField(default=0)  # TODO 直接设置方法，自动或者手动更新数量，不用到时再查

    class Meta:
        db_table = 'categorys'


class Post(BaseModel):
    title = CharField(max_length=128, index=True)

    body = TextField()
    body_html = TextField(null=True)

    category = ForeignKeyField(Category, related_name='cate', null=True)

    timestamp = DateTimeField(default=datetime.now(), index=True)
    published = BooleanField(default=1)

    reviewed = IntegerField(default=0)
    img_path = CharField(max_length=128, null=True)

    class Meta:
        db_table = 'posts'
        order_by = ('-timestamp', 'title')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.img_path is None:
            self.img_path = url_for('static', filename='img/pic0{}.jpg'.format(str(randint(1, 7))))

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        if key == 'body':  # 改body属性时，顺便更新body_html
            self.on_changed_body(self, value)

    def ping(self):  # TODO:以后改成自动调用，且不应该额外查这一次
        update = Post.update(reviewed=Post.reviewed + 1)\
            .where(Post.id == self.id)
        update.execute()
        self.save()

    @staticmethod
    def on_changed_body(target, value):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img']
        body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html5',
                     extensions=['markdown.extensions.fenced_code', 'markdown.extensions.codehilite']),
            tags=allowed_tags, strip=True
        ))  # 先将文本html化，然后清除多余的标签，最外层的函数是将URL转换成<a>
        # 手动生成img的标签
        img_pattern = re.compile('!\[(.*)\]\((.*)\)')  # markdown语法： ![description](href)
        _match = img_pattern.finditer(value)  # 查找内容
        for g in _match:
            alt, src = g.groups()
            transform_pattern = '<img alt="{alt}" src="{src}">'.format(alt=alt, src='/post_img/' + src.split('/')[-1])
            body_html = str(body_html).replace('<img>', transform_pattern, 1)

        target.body_html = body_html


