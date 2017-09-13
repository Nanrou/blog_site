from flask import g, jsonify
from flask_httpauth import HTTPBasicAuth

from . import api
from .errors import unauthorized, forbidden
from ..models import AnonymousUser, User


auth = HTTPBasicAuth()


@auth.verify_password  # 这个装饰器就是将其包裹的函数注册为验证回调函数
def verify_password(email_or_token, password):
    if email_or_token == '':
        g.current_user = AnonymousUser()
        return True
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True  # 为了让视图函数区分
        return g.current_user is not None
    u = User.query.filter_by(email=email_or_token).first()
    if not u:
        return False
    g.current_user = u
    g.token_used = False
    print('verify the password')
    return u.verify_password(password)


@api.route('/token')
def get_token():
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({'token': g.current_user.generate_auth_token(expiration=3600).decode('utf-8'),
                    'expiration': 3600})


@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')


@api.before_request  # 只在此蓝图中生效
@auth.login_required  # 验证失败就会去调用回调函数，也就是verify_password
def before_request():
    if not g.current_user.is_anonymous and not g.current_user.confirmed:
        return forbidden('Unconfirmed account')
