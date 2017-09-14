from flask import request, jsonify, g, url_for, current_app

from . import api
from .authentication import auth
from .decorators import permission_required
from .errors import forbidden
from .. import db
from ..models import Post, Permission


@api.route('/posts/', methods=['POST'])
@permission_required(Permission.WRITE_ARTICLES)
def new_post():
    _post = Post.from_json(request.json)
    _post.author = g.current_user
    db.session.add(_post)
    db.session.commit()
    return jsonify(_post.to_json(), 201,
                   {'Location': url_for('api.get_post', id_=_post.id, _external=True)})


@api.route('/posts/')
@auth.login_required
def get_posts():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.paginate(
        page, per_page=current_app.config.get('FLASKY_POSTS_PER_PAGE'),
        error_out=False
    )
    _posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_posts', page=page-1, _external=True)
    next_ = None
    if pagination.has_next:
        next_ = url_for('api.get_posts', page=page+1, _external=True)
    return jsonify({
        'posts': [post.to_json() for post in _posts],
        'prev': prev,
        'next_': next_,
        'count': pagination.total,
    })


@api.route('/posts/<int:id_>')
@auth.login_required
def get_post(id_):
    _post = Post.quert.get_or_404(id_)
    return jsonify(_post.to_json())


@api.route('/posts/<int:id_>', methods=['POST'])
@permission_required(Permission.WRITE_ARTICLES)
def edit_post(id_):
    _post = Post.query.get_or_404(id_)
    if g.current_user != _post.author and not g.current_user.can(Permission.ADMINISTER):
        return forbidden('Insufficient permissions')
    _post.body = request.json.get('body', _post.body)
    db.session.add(_post)
    db.session.commit()
    return jsonify(_post.to_json())
