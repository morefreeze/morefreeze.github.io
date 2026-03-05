---
layout: page
title: Archives
permalink: /archives/
---

<ul class="tags-box">

{% if site.posts != empty %}

{% for post in site.posts %}
{% capture this_year %}{{ post.date | date: "%Y" }}{% endcapture %}
{% unless year == this_year %}
{% assign year = this_year %}
{% unless post == site.posts.first %}
{% endunless %}
<li id="{{ year }}">{{ year }}</li>
{% endunless %}
<time datetime="{{ post.date | date:"%Y-%m-%d" }}">
{{ post.date | date:"%Y-%m-%d" }}
</time>
&raquo; <a href="{{ site.baseurl }}{{ post.url }}">{{ post.title }}</a>
{% if post.url contains '_en.html' %}
  <span class="language-tag en-tag">English</span>
{% else %}
  {% capture zh_url %}{{ post.url }}{% endcapture %}
  {% capture en_url %}{{ zh_url | replace: '.html', '_en.html' }}{% endcapture %}
  {% for p in site.posts %}
    {% capture p_url %}{{ p.url }}{% endcapture %}
    {% if p_url == en_url %}
      <span class="language-tag zh-tag">中文</span>
      {% break %}
    {% endif %}
  {% endfor %}
{% endif %}<br />
{% endfor %}

{% else %}

<span>No posts</span>

{% endif %}

</ul>
