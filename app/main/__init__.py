import re
from random import randint

from flask import Blueprint
from peewee import prefetch
from ..models import Category, Post

main = Blueprint('main', __name__)

from . import views, errors, my_tools


random_order = {'0': Category.id, '1': Category.category}


@main.app_context_processor
def inject_category():
    cc = Category.select().order_by(random_order[str(randint(0, 1))])
    return dict(cc_pr=cc)


