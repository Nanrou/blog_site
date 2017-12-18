import os
from random import randint
from datetime import datetime
import re

from flask import url_for, current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData
from peewee import CharField, IntegerField, DateTimeField, TextField, BooleanField, ForeignKeyField
from markdown import markdown
import bleach

from . import db_wrapper
from app import login_manager, cache


class BaseModel(db_wrapper.Model):
    class Meta:
        database = db_wrapper.database


class User(UserMixin, BaseModel):
    """
    以邮箱作为用户名
    加个验证码来允许回复就好了，不一定要有密码
    """

    email = CharField(max_length=32, index=True, unique=True)
    password_hash = CharField(max_length=128, null=True)

    nickname = CharField(max_length=32, unique=True, null=True)  # TODO 要判断名字是否有效
    avatar_hash = CharField(max_length=128, null=True)

    member_since = DateTimeField(default=datetime.now())
    last_seen = DateTimeField(default=datetime.now())

    confirmed = BooleanField(default=False)  # 邮箱是否认证了
    intact = BooleanField(default=False)  # 是否完整，就是是否已经设置密码了

    class Meta:
        db_table = 'users'

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self.id)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except BadData:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        self.save()
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except BadData:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        self.save()
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except BadData:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if User.select().where(User.email == new_email).first() is not None:  # 防止重复
            return False
        self.email = new_email
        self.save()
        return True

    def ping(self):
        q = User.update(last_seen=datetime.now()).where(User.id == self.id)
        q.execute()


class Admin(UserMixin, BaseModel):
    email = CharField()
    token_hash = CharField()

    @property
    def token(self):
        raise AttributeError('token is not a readable attribute')

    @token.setter
    def token(self, token):
        self.token_hash = generate_password_hash(token)

    def verify_token(self, token):
        return check_password_hash(self.token, token)


@login_manager.user_loader
def user_loader(user_id):
    return User.get(id=user_id)


# @login_manager.request_loader
# def request_loader(request):
#     email = request.form.get('email')
#     admin = Admin.select().where(Admin.email == email).first()
#     token = request.form.get('token')  # 应该再次加密，因为request中的等于是明文
#     if admin and admin.verify_token(token):
#         return admin
#     else:
#         return


class Category(BaseModel):
    category = CharField(max_length=32, index=True)
    cate = CharField(max_length=32, index=True)
    posts_count = IntegerField(default=0)

    class Meta:
        db_table = 'categorys'

    @classmethod
    def count_posts(cls):  # 直接得到分类数量，不用到时再数。可以手动或者自动去执行
        for i in range(1, cls.select(cls.id).count() + 1):
            cc = cls.get(id=i)
            cc.posts_count = cc.posts.select(Post.id).count()
            cc.save()

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self.id)


class Post(BaseModel):
    title = CharField(max_length=128, index=True)

    body = TextField()
    body_html = TextField(null=True)

    category = ForeignKeyField(Category, related_name='posts', null=True)

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

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self.id)

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        if key == 'body':  # 改body属性时，顺便更新body_html
            self.on_changed_body(self, value)

    def ping(self):
        q = Post.update(reviewed=Post.reviewed + 1) \
            .where(Post.id == self.id)  # update是class method
        q.execute()

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


class Comment(BaseModel):
    content = CharField(max_length=255)
    # content_html = TextField()  # TODO 支持markdown回复
    author = ForeignKeyField(User, related_name='comments')
    post = ForeignKeyField(Post, related_name='comments')

    timestamp = DateTimeField(default=datetime.now())

    quote_comment = ForeignKeyField('self', null=True, related_name='quote')

    class Meta:
        db_table = 'comments'
        order_by = ('timestamp',)

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self.id)

    # @cache.memoize(5 * 60)
    def all_quote(self):
        for quote in self.quote:
            yield quote
            if quote.quote.exists():
                yield from quote.all_quote()
