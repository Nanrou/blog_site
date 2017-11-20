from datetime import timedelta
from random import randint

from peewee import SelectQuery

def upupup(post):
    sq = SelectQuery(post, post.title, post.timestamp)
    for s in sq:
        if s.title.startswith('Python168'):
            q = post.update(timestamp=s.timestamp + timedelta(days=45)).where(post.title==s.title)
            q.execute()
        else:
            break
            
def add_re(post):
    sq = SelectQuery(post, post.id, post.reviewed)
    for s in sq:
        q = post.update(reviewed=s.reviewed + randint(0, 30)).where(post.id==s.id)
        q.execute()