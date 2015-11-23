---
layout: page
title: Archive
---
{% comment %}
    The groping by year is implemented following this answer <http://stackoverflow.com/a/20777475/1935366>
{% endcomment %}

{% for post in site.posts %}
  {% assign currentdate = post.date | date: "%Y" %}
  {% if currentdate != date %}
## {{ currentdate }}
    {% assign date = currentdate %} 
  {% endif %}
 * [{{ post.title}}]({{site.baseurl}}{{ post.url }})
{% endfor %}
