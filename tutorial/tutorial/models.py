# -*- coding:utf-8 -*-

from peewee import *


DATABASE = 'blog.db'

database = SqliteDatabase(DATABASE, threadlocals=True)


class BaseModel(Model):
    class Meta:
        database = database


class Entries(BaseModel):
    title = CharField()
    text = TextField()



