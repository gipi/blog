<!--
.. title: migrating to a static blogging platform
.. slug: migrating-to-static-platform
.. date: 2015-12-04 00:00:00
.. tags: meta
.. category: 
.. link: 
.. description: 
.. type: text
-->

I've always used self hosting platform for my various blogs that
I maintained during the years, the first one written using ``PHP``
(oh boy) until the last one that was developed in **Django**.

Because maintaing a blog platform is time consuming and probably
not worth doing, now I'm migrating to a static platform (i.e. [Github's pages](https://help.github.com/categories/github-pages-basics/));
a reason is that a complete blogging platform is overkilling:
I need only one account and I don't need a database, a filesystem
data storage is more than enough (morever now is a Github's problem
the performance) and the Markdown syntax is the format I'm using
the most in the last period: Indeed you can find a lot of stuffs under
my [gist](https://gist.github.com/gipi/)'s
related pages and probably some of them will become a day
a post here.

Consider also the cost of updating the infrastructure and avoid
compromission from external entities; the backup is automatic
and if some reader find a typo a *pull request* is welcome
from the [repository](https://github.com/gipi/gipi.github.io).

There are of course some aspect that I have to consider:
for the comments I will
use **Disqus** that allows me to make it indipendent from the
platform itself (I know that this esposes my reader to external
tracking but my advice is to use some *not-track-me* tecnology
like [Adblock plus](https://adblockplus.org/)).
BTW not much people commented my posts :P

Another aspect is the ``SSL``: i would like to serve the pages with a
secure connection; Github obviously doesn't have a proper certificate for
a domain owned by me, a solution could be using CloudFlare but this will
require to change the ``DNS`` servers that manage my domain and I'm not
ok with that.

So probably in the near future I will move the *compiled* pages to a
server of mine

**P.S:** if you like me have a page that is at the top domain (not, you know, a ``www`` like subdomain)
you can encounter some problems with the ``DNS`` settings for other services
like email, in that case you must set a ``A`` entry in the ``DNS`` configuration,
not a ``CNAME`` one; in this [page](https://help.github.com/articles/tips-for-configuring-an-a-record-with-your-dns-provider/)
are indicated the IP addresses to use.
<!--
After that I moved my ``DNS`` so to make it pointing by ``CNAME``
to ``gipi.github.io`` (the different domains and how Github choses them
is explained [here](https://help.github.com/articles/about-custom-domains-for-github-pages-sites/))

The final step was enabling the ``HTTPS``

 - https://blog.keanulee.com/2014/10/11/setting-up-ssl-on-github-pages.html
 - https://sheharyar.me/blog/free-ssl-for-github-pages-with-custom-domains/
-->
