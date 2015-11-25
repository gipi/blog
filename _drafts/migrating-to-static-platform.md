---
layout: post
title: 'migrating to a static blogging platform'
comments: true
---
I've always used self hosting platform for my various blogs that
I maintained during the years, the first one written using ``PHP``
(oh boy) until the last one that was developed in **Django**
and that now is used to host this pages.

Now I'm migrating to a static platform (i.e. the Github's pages)
because I havn't had enough time to maintain it from the
security point of view and updating accordingly. So, since I'm
using Github and **markdown** as first platform for publishing
stuffs I thought that will make me more productive.

A reason is that a complete blogging platform is overkilling:
I need only one account, I don't need a database, a filesystem
data storage is more than enough (morever now is a Github's problem
the performance) and the Markdown syntax is the format I'm using
the most in the last period.

Indeed you can find a lot of stuffs under my [gist](https://gist.github.com/gipi/)'s
related pages, probably some of that pages will become a day
a post here.

Another aspect of the blogging platform are the comments: I will
use **Disqus** that allows me to make it indipendent from the
platform itself (I know that this esposes my reader to external
tracking but my advice is to use some *not-track-me* tecnology
like). BTW not much people commented my posts :P

After that I moved my ``DNS`` so to make it pointing by ``CNAME``
to ``gipi.github.io`` (the different domains and how Github choses them
is explained [here](https://help.github.com/articles/about-custom-domains-for-github-pages-sites/))

The final step was enabling the ``HTTPS``

 - https://blog.keanulee.com/2014/10/11/setting-up-ssl-on-github-pages.html
 - https://sheharyar.me/blog/free-ssl-for-github-pages-with-custom-domains/
