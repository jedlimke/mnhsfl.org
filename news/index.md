---
layout: page
title: News
permalink: /news/
---

# News

{% assign result_posts = site.categories.news %}

{% for post in result_posts %}
  <article class="post-summary">
	<header class="post-header">
		<h2><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h2>
		<p class="post-meta">
			<time datetime="{{ post.date | date_to_xmlschema }}">{{ post.date | date: "%B %-d, %Y" }}</time>
		</p>
	</header>
    {% if post.excerpt %}
      <p>{{ post.excerpt | truncate: 100 }}</p>
    {% endif %}
  </article>
{% endfor %}

{% if result_posts.size == 0 %}
  <p>No news yet. Check back soon!</p>
{% endif %}
