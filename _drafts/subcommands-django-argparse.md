---
layout: post
comments: true
title: "Creating subcommand with argparse in Django"
---

```python
from argparse import ArgumentParser

from django.core.management import BaseCommand, CommandParser


class Command(BaseCommand):
    '''General purpouse command to manage thumbnail'''

    def create_parser(self, prog_name, subcommand):
        # https://github.com/allanlei/django-argparse-command/blob/master/example/management/commands/subcommand.py
        parser = super(Command, self).create_parser(prog_name, subcommand)
        # https://docs.python.org/3/library/argparse.html#sub-commands
        subparsers = parser.add_subparsers(help='sub-command help', parser_class=ArgumentParser)

        parser_list = subparsers.add_parser('list', help='list all')
        parser_resave = subparsers.add_parser('save', help='resave')

        return parser

    def handle(self, *args, **options):

        print args
        print options
```
