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

def build_filepath(post, containing_dir='_posts'):
    slug = '%s-%s.md' % (post.creation_date.strftime('%Y-%m-%d'), slugify(post.title))
    return os.path.join(containing_dir, slug)

def create_post(filepath, title, date, content, slug=None, containing_dir='_posts'):
    with open(filepath, 'w+') as f:
        f.write(u'''---
layout: post
title: '%(title)s'
comments: true
---
%(content)s
''' % {'title': title, 'content': content, })

if __name__ == '__main__':

    db = orm.Database()

    class Blog(db.Entity):
        _table_       = 'yadb_blog'
        title         = orm.Required(str)
        content       = orm.Required(str)
        status        = orm.Required(str)
        creation_date = orm.Required(datetime)

    db.bind('postgres', user=sys.argv[1], password=sys.argv[2], host=sys.argv[3], port=sys.argv[4], database='blog')

    db.generate_mapping(create_tables=False)
    with orm.db_session:
        for post in orm.select(post for post in Blog):
            print "writing '%s'" % post.title
            try:
                #print 'content:', post.content
                filepath = build_filepath(post, containing_dir='_posts' if post.status == 'pubblicato' else '_drafts')
                create_post(filepath, post.title, post.creation_date, post.content)
            except Exception as e:
                print e
                os.remove(filepath)

