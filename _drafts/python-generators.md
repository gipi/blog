---
layout: post
comments: true
title: "Introducing python's generators"
---

Any function that has the ``yield`` keyword, it's tranformed into
a generator

```python
def countdown(n):
    print "Counting down from", n
    while n > 0:
    yield n
    n -= 1
```

The first line is printed only when iterated on, not when called the function.

 - [Functional programming from python docs](https://docs.python.org/2.7/howto/functional.html)
 - [Coroutines](http://www.dabeaz.com/coroutines/)
