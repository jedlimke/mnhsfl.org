---
layout: page
title: News
permalink: /news/
---

# News

{% assign result_posts = site.categories.news %}

{% for post in result_posts %}
  <article class="post-summary">
    <h2><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h2>
    <time datetime="{{ post.date | date_to_xmlschema }}">{{ post.date | date: "%B %-d, %Y" }}</time>
    {% if post.excerpt %}
      <p>{{ post.excerpt }}</p>
    {% endif %}
    <a href="{{ post.url | relative_url }}">View news →</a>
  </article>
{% endfor %}

{% if result_posts.size == 0 %}
  <p>No news yet. Check back soon!</p>
{% endif %}
