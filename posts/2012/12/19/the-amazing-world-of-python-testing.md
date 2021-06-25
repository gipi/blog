<!--
.. title: the amazing world of python: testing
.. slug: the-amazing-world-of-python-testing
.. date: 2012-12-19 00:00:00
.. tags: python,unit tests
.. category: 
.. link: 
.. description: 
.. type: text
-->

Python is my primary language of choice when I want to program something (I'm also a fan of C but this is a sort of foolness of mine).
Between the things that make me choose python there is the way it manages to make easy to maintain our code, in this case **testing** it.

I'm an advocate of TDD (test driven development) and I think that code without tests is a useless code and writing tests in python
is simple as insert the description of API in the doctest string (this is a simplification of course).

## Doctests

Let's start with a simple module with the definition of a function able to calculate the [Fibonacci numbers](http://en.wikipedia.org/wiki/Fibonacci_number):

```python

 """
 This is the Fibonacci module. Here there is only a simple function
 the fib().

  >>> fib(10)
  55

 Since the implementation is a very simple one, don't try to calculate it
 for arguments greater than 1000 otherwise it could not return very soon.
 """

 def fib(n):
    """Return the n-th number of Fibonacci. n must be an integer
    greater than zero.

    >>> fib(1)
    1
    >>> fib(2)
    1
    >>> fib(12)
    144
    >>> fib(-4)
    Traceback (most recent call last):
        ...
    ValueError: n must be > 0
    >>> fib(10*3)
    832040
    """
    if n <= 0:
        raise ValueError("n must be > 0")

    if n == 1 or n == 2:
        return 1

    return fib(n - 1) + fib(n - 2)

```

If we save this in a file called ``fib.py`` we can call the module ``doctest`` on it by using the following command


    $ python -m doctest fib.py

With this example nothing is printed in the terminal but it's not bad, only means that the tests passed with success. It's possible to add the option ``-v`` in order to obtain a summary of the running

```
 $ python -m doctest -v fib.py
 Trying:
    fib(10)
 Expecting:
    55
 ok
 Trying:
    fib(1)
 Expecting:
    1
 ok
 Trying:
    fib(2)
 Expecting:
    1
 ok
 Trying:
    fib(12)
 Expecting:
    144
 ok
 Trying:
    fib(-4)
 Expecting:
    Traceback (most recent call last):
        ...
    ValueError: n must be > 0
 ok
 Trying:
    fib(10*3)
 Expecting:
    832040
 ok
 2 items passed all tests:
   1 tests in fib
   5 tests in fib.fib
 6 tests in 2 items.
 6 passed and 0 failed.
 Test passed.
```

There are also a set of [options](http://docs.python.org/library/doctest.html?highlight=doctest#option-flags-and-directives)
that indicate how manage the tests behaviour: for example in this case is possible to wrap the list content using two lines,
ignoring whitespaces and newlines with the option ``NORMALIZE_WHITESPACE``:

```python

 >>> a = list(xrange(20))
 >>> a # doctest: +NORMALIZE_WHITESPACE
 [0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
```

## Asserts

A special mention for the [assert](http://docs.python.org/reference/simple_stmts.html#assert)
statement that permits to insert programmatic check in your program; if you have doubts in inserting
an ``assert`` or a ``raise`` you have to know that the ``assert`` s are removed when the python
interpreter is launched with optimization activated (i.e. with flag ``-O``).

Furthemore, if you think is overkilling adding an assert that stop your code, you must note that
is better to stop your program early with a known cause that have a not-so-obvious-bug in your code.

## Test runner

The doctests are useful, but primarly for documentation purpouse (will be a post dedicated to it in the
future), so is also possible to create more elaborate stuff using the [unittest library](http://docs.python.org/library/unittest.html>);
let's start with a simple example: suppose we have a piece of our web application that will build a select menu from some entries in a database
and we want to know that this is done correctly

```python

 import sqlite3
 import tempfile
 import os
 import unittest

 def build_select(dbname):
    """Build a HTML select with the entries in the database.

    Suppose that this method belongs to another module that you want to test
    """
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()

    options = "\n".join([
        u'<option value="%s">%s</option>' % (row[0], row[0],) 
            for row in cursor.execute("SELECT nation from nations")])

    cursor.close()

    return "<select>%s</select>" % options

 class SelectTests(unittest.TestCase):
    def setUp(self):
        fd, self.db_path = tempfile.mkstemp()

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("CREATE TABLE nations (nation)")
        nations = [
            ('Italy',),
            ('Spain',),
            ('Greece',),
        ]

        cursor.executemany('INSERT INTO nations VALUES (?)', nations)
        connection.commit()
        connection.close()

    def tearDown(self):
        os.remove(self.db_path)

    def test_nations(self):
        select = build_select(self.db_path)

        self.assertEqual(u'''<select><option value="Italy">Italy</option>
 <option value="Spain">Spain</option>
 <option value="Greece">Greece</option></select>''', select)
```

If we save the code above in the file named ``select_creation.py`` we can launch the test with the
following command

```
 $ python -m unittest -v select_creation
 test_nations (select_creation.SelectTests) ... ok

 ----------------------------------------------------------------------
 Ran 1 test in 0.228s

 OK
```

All the tests are searched in the methods which name starts with ``test`` that are subclasses
of ``unittest.TestCase``; first of launch any test the method ``setUp`` is called in order to
prepare the environment for the tests (in the previous case we create a database with some entries
in it). Obviously there is a ``tearDown`` method used to clean up the environment.

It's possible to do more but I don't want to wrote a complete guide, refere to the documentation.

## Mock

In some cases is useful to *fake* objects in order to test our code against external library or not static data (think about external web service not under your direct control).

A possibility is offered by the [mock library](http://www.voidspace.org.uk/python/mock/);
if we want to test a function using the output from the twitter API, would be great to avoid the network
creating a fake response as in the following example

```python

 import requests
 import unittest
 import simplejson


 def twitter_shit(tweetid):
    """Retrieve and elaborate a tweet

    """
    url = "https://api.twitter.com/1/statuses/show.json?id=%s" % tweetid
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception("obtained %d from server" % response.status_code)

    json = simplejson.loads(response.text)

    return "%s: %s" % (json["user"]["screen_name"], json["text"],)

 class TwitterTests(unittest.TestCase):
    def test_twitter_shit(self):
        fake_tweet = """{"created_at":"Mon Oct 08 08:34:49 +0000 2012","id":255224718150492162,"id_str":"255224718150492162","text":"hello world","user":{"id":378779203,"screen_name":"user1"}}"""

        with mock.patch("requests.get") as mocked_get:
            mocked_get.return_value.status_code = 200
            mocked_get.return_value.text = fake_tweet

            response = twitter_shit("whatever")

            self.assertEqual(response, "user1: hello world")
```

In this case we simply *patch* with a [context manager](http://www.python.org/dev/peps/pep-0343/) the
``get()`` method to return a status code equal to 200 with
a predetermined text. At this point is easy to check that the response is parsed correctly.

This is not the only available library, use google to find them and report in the comments if you think there are alternatives :P.

## Coverage

Not only the tests are important, but also how they are written and which lines of code will be executed: a test missing some branching point (roughly speaking one of an ``if`` condition) or some condition, is a test that gives false sense of security. For code more elaborated and complex that the fibonacci example (think for example to a Django project) we need to know exactly how our code is tested.

This is possible using the ``coverage`` module that will print a report indicating which lines of code are executed and which branch of execution are missing. Let's try to use this module: first of all install it


    $ pip install coverage

Since with ``coverage`` we need to launch directly the tests (i.e. without the ``-m doctest`` command line option) we add the following lines at the bottom of ``fib.py``

```python

 if __name__ == "__main__":
    import doctest
    doctest.testmod()
```

(they simply launch the tests when we do ``./fib.py``) and execute the following command

    $ coverage run ./fib.py

This will create a file named ``.coverage`` in the working directory. Now is possible to have a report relative to our test

```
 $ coverage report
 Name    Stmts   Miss  Cover
 ---------------------------
 fib        11      0   100%
```

If we want a real report with each line annotated is possible to create an HTML one using

    $ coverage html

It's worth noting that is possible to use it with your django project following [this instructions](http://www.darkcoding.net/software/code-coverage-in-django-with-coverage-and-django-jenkins/).