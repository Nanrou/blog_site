import os
from flask import render_template, Response, send_file, request
from playhouse.flask_utils import get_object_or_404, PaginatedQuery

from . import main
from ..models import Post
from .my_tools import MyPaginatedQuery


@main.route('/')
def home():
    pagination = PaginatedQuery(Post, 8, check_bounds=True)

    _posts = pagination.get_object_list()

    return render_template('main/home.html', pagination=pagination, posts=_posts)


@main.route('/post', defaults={'id_': 1})
@main.route('/post/<int:id_>')
def post(id_):
    _post = get_object_or_404(Post.select().where(Post.published == 1), (Post.id == id_))
    _post.ping()  # 手动刷新

    _public_posts = Post.select(Post.id, Post.title).where(Post.published == 1)

    _prev = _public_posts.order_by(Post.id).where(Post.id > _post.id).first()
    _next = _public_posts.where(Post.id < _post.id).first()
    return render_template('main/post.html', post=_post, next_post=_next, prev_post=_prev)


@main.route('/post_img/<string:img_id>')  # 图片的导航
def post_img(img_id):
    img_path = os.path.join('post_img', img_id)
    return send_file(img_path, conditional=True)  # send_file是生成响应的，显式指定conditional才会进行条件判断

