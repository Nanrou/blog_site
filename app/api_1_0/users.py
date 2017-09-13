from flask import jsonify, request, current_app, url_for
from . import api
from ..models import User, Post


@api.route('/users/<int:id_>')
def get_user(id_):
    user = User.query.get_or_404(id_)
    return jsonify(user.to_json())


@api.route('/users/<int:id_>/posts/')
def get_user_posts(id_):
    user = User.query.get_or_404(id_)
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_user_posts', id=id_, page=page-1,
                       _external=True)
    next_ = None
    if pagination.has_next_:
        next_ = url_for('api.get_user_posts', id=id_, page=page+1,
                        _external=True)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next_': next_,
        'count': pagination.total
    })


@api.route('/users/<int:id_>/timeline/')
def get_user_followed_posts(id_):
    user = User.query.get_or_404(id_)
    page = request.args.get('page', 1, type=int)
    pagination = user.followed_posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_user_followed_posts', id=id_, page=page-1,
                       _external=True)
    next_ = None
    if pagination.has_next_:
        next_ = url_for('api.get_user_followed_posts', id=id_, page=page+1,
                        _external=True)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next_': next_,
        'count': pagination.total
        })
