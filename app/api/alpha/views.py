from datetime import datetime

from flask import request, jsonify

from . import api
from app.models import Post

required_files = ['title', 'timestamp', 'body', 'category']

cate_dict = {'Django': 1, '日常踩坑': 2, '读书笔记': 3, 'LeetCode': 4, 'python': 5, '一些翻译': 6, 'linux': 7}


@api.route('/posts', methods=['POST'])
def new_post():
    post_json = request.json
    if all(files in post_json.keys() for files in required_files) and len(post_json):
        _time = datetime.strptime(post_json.get('timestamp'), '%Y-%m-%d %H:%M')
        pp = Post.create(**{'title': post_json.get('title'), 'body': post_json.get('body'), 'timestamp': _time,
                            'category': cate_dict[post_json.get('category')]})
        pp.save()
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'wrong type'})


@api.route('/hello')
def hello():
    return jsonify({'status': 'success'})
