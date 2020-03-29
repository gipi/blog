Future static blogging: https://ktln2.org/

## Testing


    $ make install_dependencies
    $ make

## Authoring guide

### Work in progress

Posts with the tag ``WIP`` are uncomplete posts, the show a message to the top
indicating this state.

### Images

```
![]({{ site.baseurl }}/public/images/certificates/certificates-wizard.png)
```

### Video

    {% include video.html video_url="https://www.video.com" %}

### Link to another post

    {% post_url file-name-wo-md-extension %}

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
