from flask import render_template, redirect, request, url_for, flash, Request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from peewee import IntegrityError

from . import auth
from .forms import LoginForm, RegistrationForm
from ..models import User
from ..email import send_email
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
                return jsonify({
                    'status': 'success',
                    'next_url': request.args.get('next')  or url_for('main.index'),
                })

    return jsonify({
        'status': 'error',
        'error_msg': '用户名或密码错误喔',
    })


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.home'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == 'POST':
        if form.validate_on_submit():  # TODO 在前端验证格式
            try:
                user = User.create(
                    email=form.email.data,
                    password=form.password.data,
                )
                token = user.generate_confirmation_token()
                send_email(user.email, 'Confirm Your Account',
                           'email/confirm', user=user, token=token)
            except IntegrityError:
                pass  # TODO 针对冲突怎么处理
            flash('确认邮件已经发送到您的邮箱了哦')
            return redirect(url_for('main.index'))
        else:  # 注意这个重定向
            return redirect(url_for('auth.register'))
    return render_template('auth/register.html', form=form)

