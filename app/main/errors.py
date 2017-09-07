from flask import render_template
from . import main


@main.app_errorhandler(404)  # 若只使用errorhandler，则只在本蓝图内，而用app的话则是全局
def page_not_found(e):
    return render_template('404.html'), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
