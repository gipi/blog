---
layout: post
title: "Django and stuffs you don't expect"
comments: true
---
I worked with Django for a lot of years but there are things that puzzles me and bites me in the ass

## Saving Multi-table inheritance

You probably know that exists a kind of ihneritance called **multi-table**
where the subclass has a ``OneToOneField`` pointing to the parent; well, take
for example this two models definition

```python
class Place(models.Model):
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=80)

class Restaurant(Place):
    place = models.OneToOneField(Place, parent_link=True, related_name='restaurant')
    serves_hot_dogs = models.BooleanField()
    serves_pizza = models.BooleanField()
```
If you, for some reason, want to create an instance of ``Restaurant`` with an explicit
parent you can try to issue the following code

```python
child = Restaurant(place_ptr=place)
child.save()
```
but surprise, an exception happens! exists also a [ticket](https://code.djangoproject.com/ticket/7623>) about this stuffs
that presents also a solution (honestly I don't know if has some drawbacks,
I used it in some projects and the database haven't keep fire)

```python
child = Restaurant(place_ptr=place)
child.save_base(raw=True)
```

## Multiple filters()

The Django's ORM is the most fascinating piece of magic, with the simplicity of write a query using easy to read python-like syntax;
by the way sometimes what you obtain is not what you expect when are involved foreign keys: normally you can concatenate ``filter()``
calls and you obtain conditions ``AND`` ed together. Instead if you are filtering with respect to attribute of foreign key and you
use concatenation of the filter() calls then you obtain

```sql
 SELECT "deal_dealbase".*
 FROM "deal_dealgroup"
     INNER JOIN "deal_dealbase" ON ( "deal_dealgroup"."dealbase_ptr_id" = "deal_dealbase"."id" )
     INNER JOIN "deal_dealsession" ON ( "deal_dealbase"."id" = "deal_dealsession"."deal_id" )
     LEFT OUTER JOIN "deal_bet" ON ( "deal_dealsession"."id" = "deal_bet"."session_id" )
 WHERE (
     "deal_dealsession"."start" < 2015-04-27 14:01:47.316449+00:00
     AND "deal_dealsession"."end" > 2015-04-27 14:01:47.316449+00:00
     AND "deal_bet"."id" IS NULL
     AND "deal_dealbase"."attiva" = True
 )

```sql

 SELECT "deal_dealgroup".*
 FROM "deal_dealgroup"
     INNER JOIN "deal_dealbase"    ON ( "deal_dealgroup"."dealbase_ptr_id" = "deal_dealbase"."id" )
     INNER JOIN "deal_dealsession" ON ( "deal_dealsession"."deal_id" = "deal_dealbase"."id" )
     LEFT OUTER JOIN "deal_bet" T8 ON ( "deal_dealsession"."id" = T8."session_id" )
 WHERE (
     "deal_dealsession"."start" < '%s'
     AND "deal_dealsession"."end" > '%s'
     AND "deal_dealbase"."attiva" = true
     AND T8."status" = %d
 )
```

 - [Ticker 18437](https://code.djangoproject.com/ticket/18437)

## Permissions migration

## Proxy permissions

 - [Ticket 11154](https://code.djangoproject.com/ticket/11154)

## Validation on model saving

This is strange: if you have some validation on the fields of a model, it's not applied
when an instance is saved.

 - [Ticket 13100](https://code.djangoproject.com/ticket/13100)
