---
layout: post
comments: true
title: "RHME2 AVR filesystem writeup"
tags: [AVR, writeup, crypto]
---

The following post is a little cheating from my part since I haven't
directly solved this challenge but I think is a good idea to write down
what went wrong with my reasoning.

## Introduction

The challenge started with the following list of token and files that can be
accessed using them

| token                                       | filename                       |
|---------------------------------------------|--------------------------------|
|``96103df3b928d9edc5a103d690639c94628824f5`` | cat.txt                        |
|``933d86ae930c9a5d6d3a334297d9e72852f05c57`` | cat.txt,finances.csv           |
|``83f86c0ba1d2d5d60d055064256cd95a5ae6bb7d`` | cat.txt,finances.csv,joke.txt  |
|``ba2e8af09b57080549180a32ac1ff1dde4d30b14`` | cat.txt,joke.txt               |
|``0b939251f4c781f43efef804ee8faec0212f1144`` | finances.csv                   |
|``4b0972ec7282ad9e991414d1845ceee546eac7a1`` | finances.csv,joke.txt          |
|``715b21027dca61235e2663e59a9bdfb387ca7997`` | joke.txt                       |

First of all we can note that all the tokens are composed of 40 hexadecimal digits,
since this is a crypto challenge we imagine the ``sha1`` of something is involved
with the result.

## Wrong path

My initial guess was that the argument of the ``sha1`` function was a concatenation
of some guessable info about the files; when you connect to the board via serial console
I obtain a terminal with the following output

```
RHMeOS file API
Files in system:
   
drwxrwxr-x remote remote 4096 sep  1 .
drwxrwxr-x remote remote 4096 sep  1 ..
-r--r--r-- remote remote   87 sep 14 cat.txt
-r--r--r-- remote remote   47 sep 16 finances.csv
-r--r--r-- remote remote    3 sep 14 joke.txt
-rw------- root   root     37 jan  5 passwd
-rw------- root   root      8 jan  1 pepper
   
 Request?

>>
```

so I wrote a script that simply try to build all the combination of usable information,
like ``user``, ``group``, ``filename``.

```python
'''
Suppose the token generating function is built from the following information

 - user (remote or its id)
 - filename (here will use 'cat.txt')
 - some separator for the values
 - number of file
'''
import sys
import hashlib
import itertools


SEPARATORS = [
    ':',
    '#',
    '\x00',
    '\t',
    '\n',
    '|',
    '+',
    ',',
    '.',
    '/',
    '\\',
    '@',
    ';',
    '%',
    '$',
    ' ',
    '&',
    '!',
    '',
]

TARGET = '96103df3b928d9edc5a103d690639c94628824f5'

FILENAME = 'cat.txt'
USER = 'remote'
GROUP = 'remote'
USERID = xrange(1001)
GROUPID = xrange(1001)
N_FILES = '1'
PERMISSIONS = '0444'


'''
Add generic transformation, like reversing the string
Add iterables as list element
Add function that returns something based on other elements
'''

def build_list(it):
    '''if it's an iterable, iter it'''
    r = []
    for i in it:
        if hasattr(i, '__iter__'):
            _i = iter(i)
            r.append(next(_i))
        else:
            r.append(i)

    yield r

if __name__ == '__main__':
    l = [N_FILES, FILENAME, GROUP, USER, USERID, GROUPID, PERMISSIONS]

    for ll in build_list(l):
        for length in xrange(1, len(ll) + 1):
            for ls in itertools.combinations(ll, length):
                for l_perm in itertools.permutations(ls):
                    for separator in SEPARATORS:
                        for eol in SEPARATORS:
                            value = separator.join(l_perm) + eol
                            h = hashlib.new('sha1')
                            h.update(value)
                            hash_value = h.hexdigest()

                            print '%s\t%s\t%s\t%s' % (l_perm, repr(separator), repr(eol), hash_value)

                            if hash_value == TARGET or hash_value[::-1] == TARGET:
                                print l_perm, repr(separator)
                                sys.exit(0)
```

Bad enough this approach didn't worked at all.

## The right path

One week ago [Liveoverflow]() posted a video with the solution of this challenge,
revealing that is possible to use a **length extension attack** with this hashing scheme,
a well known fact about ``sha1``.

This attack allows to use an already known hash value of a given data to calculate
the hash of a new block of data having the old as prefix.

This is important because the argument used for the ``sha1`` in this challenge is
in the following form

    <secret><filename1:filename2:...:filenameN>

So the reason for which my attempts failed was that I guessed incorrectly of course
and also that a bruteforce attack is infeasable (with a secret long enough).

We know that for the string ``<secret>cat.txt`` the hash is ``96103df3b928d9edc5a103d690639c94628824f5``,
but now it's possible to calculate the ``sha1`` for something like

    <secret>cat.txt<garbage>:passwd


## Link

 - [FIPS 180-4](http://csrc.nist.gov/publications/fips/fips180-4/fips-180-4.pdf) Secure Hash Standard (SHS)
