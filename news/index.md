---
layout: page
title: News
permalink: /news/
---

# League News & Announcements

{% for post in site.posts %}
  <article class="post-summary">
    <h2><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h2>
    <time datetime="{{ post.date | date_to_xmlschema }}">{{ post.date | date: "%B %-d, %Y" }}</time>
    {% if post.categories %}
      <span class="post-categories">
        {% for category in post.categories %}
          <span class="category">{{ category }}</span>
        {% endfor %}
      </span>
    {% endif %}
    <p>{{ post.excerpt }}</p>
    <a href="{{ post.url | relative_url }}">Read more →</a>
  </article>
{% endfor %}

{% if site.posts.size == 0 %}
  <p>No news posts yet. Check back soon!</p>
{% endif %}
