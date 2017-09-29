from flask import render_template, redirect, request, url_for, flash, Request, jsonify
from flask_login import login_user, logout_user, login_required, current_user

from . import auth
from .forms import LoginForm, RegistrationForm
from ..models import User
from app import login_manager, db_wrapper


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()  # 更新最后登陆时间
        # if not current_user.confirmed and request.endpoint[:5] != 'auth.':
         #   return redirect(url_for('auth.unconfirmed'))

            
@auth.route('/login')
def login():
    form = LoginForm()
    return render_template('auth/login.html', form=form)


@auth.route('/login', methods=['POST'])
def verify_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.select().where(User.email == form.email.data).first()
        if user:
            if not user.intact or user.verify_password(form.password.data):  # 没密码 或者验证了密码
                login_user(user, form.remember_me.data)
                return redirect(request.args.get('next') or request.headers.get('Referer') or url_for('main.index'))
    else:
        return jsonify({
            'error_msg': '用户名或密码错误喔',
        })



