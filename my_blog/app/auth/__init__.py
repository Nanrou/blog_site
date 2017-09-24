import re
from random import randint

from flask import Blueprint
from peewee import prefetch
from ..models import Category, Post

auth = Blueprint('auth', __name__)

from . import forms
