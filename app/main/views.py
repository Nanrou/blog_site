from datetime import datetime

from flask import current_app, render_template, session, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from . import main
from .forms import NameForm, EditProfileForm, EditProfileAdminForm
from .. import db
from ..models import User, Role
from ..email import send_email
from ..decorators import admin_required, permission_required
from ..models import Permission


@main.route('/', methods=['GET', 'POST'])
def index():
    # app = current_app._get_current_object()
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
            # if app.config['FLASKY_ADMIN']:
            #     send_email(app.config['FLASKY_ADMIN'], 'New User',
            #                'mail/user', user=user)
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('main.index'))
    return render_template('index.html',  current_time=datetime.utcnow(),
                           form=form, name=session.get('name'), known=session.get('known', False))


@main.route('/secret')
@login_required
def secret():
    return 'Only authenticated users are allowed!'


@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return 'For admin'


@main.route('/moderator')
@login_required
@permission_required(Permission.MODERATE_COMMITS)
def for_moderators_only():
    return 'For comment moderators'


@main.route('/user/<username>')
def user(username):
    u = User.query.filter_by(username=username).first()
    if u is None:
        abort(404)
    return render_template('user.html', user=u)


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
