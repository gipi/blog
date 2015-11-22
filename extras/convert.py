# encoding: utf-8
"""
Script to convert all posts to Jekyll format.

We are going to use PonyORM <https://docs.ponyorm.com/>.
"""
import sys
import os
from slugify import slugify
from datetime import datetime

from pony import orm

def create_post(title, date, content, slug=None, containing_dir='_posts'):
    slug = slug or '%s-%s.md' % (date.strftime('%Y-%m-%d'), slugify(title))
    filepath = os.path.join(containing_dir, slug)
    with open(filepath, 'w+') as f:
        f.write(u'''---
layout: post
title: %(title)s
---
%(content)s
''' % {'title': title, 'content': content, })

if __name__ == '__main__':

    db = orm.Database()

    class Blog(db.Entity):
        _table_       = 'yadb_blog'
        title         = orm.Required(str)
        content       = orm.Required(str)
        creation_date = orm.Required(datetime)

    db.bind('postgres', user=sys.argv[1], password=sys.argv[2], host=sys.argv[3], port=sys.argv[4], database='blog')

    db.generate_mapping(create_tables=False)
    with orm.db_session:
        for post in orm.select(post for post in Blog):
            print "writing '%s'" % post.title
            try:
                #print 'content:', post.content
                create_post(post.title, post.creation_date, post.content)
            except Exception as e:
                print e

