import os
from flask import render_template, Response, send_file, request, flash, redirect, jsonify, abort
from playhouse.flask_utils import get_object_or_404, PaginatedQuery
from flask_login import login_required, current_user


from . import main
from ..models import Post, Category, Comment
from .forms import CommentForm, RegistrationForm
from .my_tools import MyPaginatedQuery, another_month_dict, product_month


@main.route('/')
def home():
    pagination = PaginatedQuery(Post.select(Post, Category).join(Category), 8, check_bounds=True)

    _posts = pagination.get_object_list()

    return render_template('main/home.html', pagination=pagination, posts=_posts)


@main.route('/post', defaults={'id_': 1})
@main.route('/post/<int:id_>')
def post(id_):
    _post = get_object_or_404(Post.select().where(Post.published == 1), (Post.id == id_))
    _post.ping()  # 手动刷新。因为这个操作是直接更改数据库的，不对现在的这个实例产生影响

    _public_posts = Post.select(Post.id, Post.title).where(Post.published == 1)

    _prev = _public_posts.order_by(Post.id).where(Post.id > _post.id).first()
    _next = _public_posts.where(Post.id < _post.id).first()

    comments = _post.comments.where(Comment.quote_comment.is_null())

    if current_user.is_authenticated:
        form = CommentForm()
    else:
        form = RegistrationForm()

    return render_template('main/post.html', post=_post,
                           next_post=_next, prev_post=_prev, comments=comments,
                           form=form,)


@main.route('/post/<int:id_>', methods=['POST'])
def submit_comment(id_):  # TODO 处理ajax
    if current_user.is_authenticated:
        form = CommentForm()  # TODO
    else:
        form = RegistrationForm()
        flash('mission complete')
    return render_template(request.url)


@main.route('/post_img/<string:img_id>')  # 图片的导航
def post_img(img_id):
    img_path = os.path.join('post_img', img_id)
    return send_file(img_path, conditional=True)  # send_file是生成响应的，显式指定conditional才会进行条件判断


@main.route('/getcalendar', methods=['POST'])
def get_calendar():
    month, prev = request.form.get('month'), request.form.get('prev')
    month = another_month_dict.get(month)
    if prev == 'true':
        month -= 1
        if month < 1:
            month = 12
    else:
        month += 1
        if month > 12:
            month = 1
    try:
        calendar = product_month(month)
    except KeyError:
        abort(404)
    else:
        return jsonify(calendar=calendar)


@main.route('/search')
def search():
    cate_dict = {'Django': 1, 'daily': 2, 'booknote': 3, 'leetcode': 4, 'python': 5, 'translation': 6, 'linux': 7}

    wd = request.args.get('wd')
    if wd in cate_dict:
        res = Category.get(id=cate_dict[wd]).posts
        return render_template('main/search_result.html', res=res)
