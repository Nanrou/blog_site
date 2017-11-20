from flask import render_template, redirect, request, url_for, flash, Request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from peewee import IntegrityError

from . import auth
from .forms import LoginForm, RegistrationForm, ChangeEmailForm, ChangePasswordForm, PasswordResetRequestForm, PasswordResetForm
from ..models import User
from ..email import send_email


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()  # 更新最后登陆时间
        if not current_user.confirmed and request.endpoint[:5] != 'auth.':
            return redirect(url_for('auth.unconfirmed'))

            
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
                    'next_url': request.args.get('next') or url_for('main.index'),
                })

    return jsonify({
        'status': 'error',
        'error_msg': '用户名或密码错误喔',
    })


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    # flash('You have been logged out.')
    return redirect(url_for('main.home'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == 'POST':
        if form.validate_on_submit():  # TODO 在前端验证格式
            try:
                user = User.create(
                    email=form.email.data,
                    nickname=form.nickname.data,
                    password=form.password.data,
                )
                user.save()
                token = user.generate_confirmation_token()
                send_email(user.email, 'Confirm Your Account',
                           'email/confirm', user=user, token=token)
            except IntegrityError:
                pass  # TODO 针对冲突怎么处理
            flash('确认邮件已经发送到您的邮箱了哦')
            return redirect(url_for('auth.login'))
        else:  # 注意这个重定向
            flash('请输入正确资料')
            return redirect(url_for('auth.register'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('你已经成功激活你的账号了')
    else:
        flash('嗯，好像出错了，请稍后再试一次')
    return redirect(url_for('main.index'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            q = User.update(password=form.old_password.data).where(User.email == current_user.email)
            q.execute()
            flash('已更新密码.')
            return redirect(url_for('main.index'))
        else:
            flash('无效密码.')
    return render_template("auth/change_password.html", form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.select().where(User.email == form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, 'Reset Your Password',
                       'email/reset_password',
                       user=user, token=token,
                       next=request.args.get('next'))
        flash('请登陆您的邮箱进行下一步操作')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.select().where(User.email == form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, 'Confirm your email address',
                       'email/change_email',
                       user=current_user, token=token)
            flash('请登陆新邮箱激活~')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.')
    return render_template("auth/change_email.html", form=form)


@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('已更新邮箱地址')
    else:
        flash('嗯？好像出错了，请稍后再试一次')
    return redirect(url_for('main.index'))
