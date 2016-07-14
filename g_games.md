---
layout: page
title: Games
permalink: /games/
---

<ul class="tags-box">

{% if site.posts != empty %}

    {% for post in site.posts %}
        {% if post.category == "game" %}
            {% if post.rating == null %}
                - / 10
            {% else %}
                {{ post.rating }} / 10
            {% endif %}
            <a href="{{ site.baseurl }}{{ post.url }}">{{ post.title | capitalize }}</a><br />
        {% endif %}
    {% endfor %}

{% else %}

<span>No posts</span>

{% endif %}

</ul>
