Repository containing my personal blog; you can find a live version at https://ktln2.org/.

It's a static site generated using [nikola](https://getnikola.com/).

## Getting started

```
$ pip install -r requirements.txt
```

## Authoring guide

### Work in progress

Posts with the tag ``WIP`` are uncomplete posts, the show a message to the top
indicating this state.

### Images

```
![]({{ site.baseurl }}/public/images/certificates/certificates-wizard.png)
```

### Footnotes

```
Generally NMOS are faster than PMOS [^1]

[^1]: p26-27 nanometer CMOS ICs
```

### Video

    {% include video.html video_url="https://www.video.com" %}

### Link to another post

You can use the syntax ``link://<kind>/<name>``, like
``link://slug/slug-of-your-post``. More information [here](https://getnikola.com/path-handlers.html).

### Mathematics

Wrap your ``TeX`` inside a ``<div>`` so to avoid the interpretation
of characters like ``_`` in Markdown and their escaping.

### Include Github code

{% github_sample_ref gipi/anet-scanner/blob/cdab1597b5c753efa4afe278b54f1ae806002d57/anet/serial.py %}
{% highlight python %}
{% github_sample gipi/anet-scanner/blob/cdab1597b5c753efa4afe278b54f1ae806002d57/anet/serial.py %}
{% endhighlight %}

## Links

 - https://adereth.github.io/blog/2013/11/29/colorful-equations/
 - http://www.minddust.com/post/tags-and-categories-on-github-pages/
 - https://codinfox.github.io/dev/2015/03/06/use-tags-and-categories-in-your-jekyll-based-github-pages/
 - [Liquid reference](https://docs.shopify.com/themes/liquid)
 - [Liquid documentation](https://github.com/Shopify/liquid/wiki/Liquid-for-Designers)
