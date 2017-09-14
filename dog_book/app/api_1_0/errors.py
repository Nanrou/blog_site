from flask import jsonify

from . import api
from ..exceptions import ValidationError


def bad_request(message):
    response = jsonify({'error': 'bad request', 'message': message})
    response.status_code = 400
    return response


def unauthorized(message):
    response = jsonify({'error': 'unauthorized', 'message': message})
    response.status_code = 401
    return response


def forbidden(message):
    resp = jsonify({'error': 'forbidden', 'message': message})
    resp.status_code = 403
    return resp


@api.errorhandler(ValidationError)  # 处理特定异常
def validation_error(e):
    return bad_request(e.args[0])
