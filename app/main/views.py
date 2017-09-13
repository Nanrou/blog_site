
from flask import current_app, render_template, redirect, url_for, flash, abort, request, make_response
from flask_login import login_required, current_user
from flask_sqlalchemy import get_debug_queries

from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostForm, CommentForm
from .. import db
from ..models import User, Role, Post, Comment
from ..decorators import admin_required, permission_required
from ..models import Permission


@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['FLASKY_DB_QUERY_TIMEOUT']:
            current_app.logger.warning(
                'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n'
                % (query.statement, query.parameters, query.duration,
                   query.context))
    return response


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        _post = Post(body=form.body.data,
                     author=current_user._get_current_object())  # 拿到真正的用户对象
        db.session.add(_post)
        db.session.commit()
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)

    _show_followed = False
    if current_user.is_authenticated:
        _show_followed = bool(request.cookies.get('show_followed', ''))
    if _show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config.get('FLASKY_POSTS_PER_PAGE'),
        error_out=False,
    )
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts, pagination=pagination,
                           show_followed=_show_followed)


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('main.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('main.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp


@main.route('/secret')
@login_required
def secret():
    return 'Only authenticated users are allowed!'


@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return 'For admin'


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config.get('FLASKY_COMMENTS_PER_PAGE'),
        error_out=False
    )
    comments = pagination.items
    return render_template('moderate.html', comments=comments,
                           pagination=pagination, page=page)


@main.route('/moderate/enable/<int:id_>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id_):
    comment = Comment.query.get_or_404(id_)
    comment.disabled = False
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('main.moderate',
                    page=request.args.get('page', 1)))


@main.route('/moderate/disable/<int:id_>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id_):
    comment = Comment.query.get_or_404(id_)
    comment.disabled = True
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('main.moderate',
                            page=request.args.get('page', 1)))


@main.route('/user/<username>')
def user(username):
    u = User.query.filter_by(username=username).first()
    if u is None:
        abort(404)
    posts = u.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html', user=u, posts=posts)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('main.user', username=current_user.username))
    form.name.data = current_user.name  # 初始化表格来显示
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id_>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id_):
    u = User.query.get_or_404(id_)
    form = EditProfileAdminForm(user=u)
    if form.validate_on_submit():
        u.email = form.email.data
        u.username = form.username.data
        u.confirmed = form.confirmed.data
        u.role = Role.query.get(form.role.data)
        u.name = form.name.data
        u.location = form.location.data
        u.about_me = form.about_me.data
        db.session.add(u)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=u.username))
    form.email.data = u.email
    form.username.data = u.username
    form.confirmed.data = u.confirmed
    form.role.data = u.role_id
    form.name.data = u.name
    form.location.data = u.location
    form.about_me.data = u.about_me
    return render_template('edit_profile.html', form=form, user=u)


@main.route('/post/<int:id_>', methods=['GET', 'POST'])
def post(id_):
    p = Post.query.get_or_404(id_)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data, post=p, author=current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been published.')
        return redirect((url_for('main.post', id_=p.id, page=-1)))
    page = request.args.get('page', 1, type=int)
    if page == -1:  # 显示最后一页
        page = (p.comments.count() - 1) // \
               current_app.config.get('FLASKY_COMMENTS_PER_PAGE', 20) + 1  # // 整除
    pagination = p.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config.get('FLASKY_COMMENTS_PER_PAGE'),
        error_out=False
    )
    comments = pagination.items
    return render_template('post.html', posts=[p], form=form,
                           comments=comments, pagination=pagination)  # 这个posts是为了其他兼容其他视图函数，因为模版接收的是列表形式


@main.route('/edit/<int:id_>', methods=['GET', 'POST'])
def edit(id_):
    p = Post.query.get_or_404(id_)
    if current_user != p.author and not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        p.body = form.body.data
        db.session.add(p)
        db.session.commit()
        flash('The post has been updated.')
        return redirect(url_for('main.post', id_=p.id))
    form.body.data = p.body
    return render_template('edit_post.html', form=form)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    u = User.query.filter_by(username=username).first()
    if u is None:
        flash('Invalid user.')
        return redirect(url_for('main.index'))
    if current_user.is_following(u):
        flash('You are already following this user.')
        return redirect(url_for('main.user', username=username))
    current_user.follow(u)
    flash('You are now following %s.' % username)
    return redirect(url_for('main.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    u = User.query.filter_by(username=username).first()
    if u is None:
        flash('Invalid user.')
        return redirect(url_for('main.index'))
    if not current_user.is_following(u):
        flash('You are already unfollowing this user.')
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(u)
    flash('You are now unfollowing %s.' % username)
    return redirect(url_for('main.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    u = User.query.filter_by(username=username).first()
    if u is None:
        flash('Invalid user.')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    pagination = u.followers.paginate(
        page, per_page=current_app.config.get('FLASKY_FOLLOWERS_PER_PAGE'),
        error_out=False,
    )
    follows = [{'user': item.follower, 'timestamp': item.timestamp} for item in pagination.items]
    return render_template('followers.html', user=u, title='Followers of',
                           endpoint='main.followers', pagination=pagination,
                           follows=follows)


@main.route('/followed-by/<username>')
def followed_by(username):
    u = User.query.filter_by(username=username).first()
    if u is None:
        flash('Invalid user.')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    pagination = u.followed.paginate(
        page, per_page=current_app.config.get('FLASKY_FOLLOWED_PER_PAGE'),
        error_out=False,
    )
    follows = [{'user': item.followed, 'timestamp': item.timestamp} for item in pagination.items]
    return render_template('followers.html', user=u, title='Followed of',
                           endpoint='main.followed_by', pagination=pagination,
                           follows=follows)  # 模版是复用follower的
