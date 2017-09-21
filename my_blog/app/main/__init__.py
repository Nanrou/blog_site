from random import randint

from flask import Blueprint
from peewee import prefetch
from ..models import Category, Post

main = Blueprint('main', __name__)

from . import views, errors, my_filter


random_order = {'0': Category.id, '1': Category.category}

@main.app_context_processor
def inject_category():
    cc = Category.select().order_by(random_order[str(randint(0, 1))])
    pp = Post.select(Post.id, Post.category)
    return dict(cc_pr=prefetch(cc, pp))
