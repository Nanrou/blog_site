import os
from flask import render_template, Response, send_file, request
from playhouse.flask_utils import get_object_or_404, PaginatedQuery

from . import main
from ..models import Post


@main.route('/')
def home():

    page = request.args.get('page', 1, type=int)
    pagination = PaginatedQuery(Post, 8, page, check_bounds=True)

    _posts = pagination.get_object_list()

    return render_template('main/home.html', pagination=pagination, posts=_posts)


@main.route('/post', defaults={'id_': 1})
@main.route('/post/<int:id_>')
def post(id_):
    _post = get_object_or_404(Post.select().where(Post.published == 1), (Post.id == id_))
    _post.ping()
    
    pagination = PaginatedQuery(Post.select(Post.id, Post.title).where(Post.published == 1), 1, _post.id, check_bounds=True)
    
    return render_template('main/post.html', post=_post, pagination=pagination)


@main.route('/post_img/<string:img_id>')  # 图片的导航
def post_img(img_id):
    img_path = os.path.join('post_img', img_id)
    return send_file(img_path, conditional=True)  # send_file是生成响应的，显式指定conditional才会进行条件判断

