from flask import render_template
from playhouse.flask_utils import get_object_or_404

from . import main
from ..models import Post


@main.route('/')
def home():
    return render_template('main/home.html')


@main.route('/post', defaults={'id_': 2})
@main.route('/post/<int:id_>')
def post(id_):
    public_posts = Post.select().where(Post.published == 1)
    _post = get_object_or_404(public_posts, (Post.id == id_))
    return render_template('main/post.html', post=_post)
