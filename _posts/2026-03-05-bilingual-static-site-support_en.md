---
layout: post
title: "Best Practices for Bilingual Static Site Support - Chinese/English Example"
description: "Sharing technical details and best practices for implementing Chinese/English bilingual support in Jekyll static sites"
category: devops
comments: true
tags: [devops, jekyll, static-site, bilingual, i18n]
---
{% include JB/setup %}

* Table of Contents
{:toc}

## Introduction

Imagine one of your technical articles being discovered by a developer abroad, but they can't grasp its essence due to language barriers. Or an international reader wants to engage with your ideas but gives up because of language differences.

In today's globalized world, multilingual support isn't just a nice-to-have—it's a necessity. However, many multilingual implementations for static sites are either too complex or not elegant enough. Today, I want to share a simple, intuitive, and easy-to-maintain solution based on my personal blog implementation.

## Core Implementation Ideas

### 1. File Naming Convention: Language in the Filename

I use a simple and intuitive approach to distinguish language versions: filename suffixes.

- **Chinese articles**: `yyyy-mm-dd-title.md`
- **English articles**: `yyyy-mm-dd-title_en.md`

This approach offers three key advantages:
<!--more-->
- **Intuitive Recognition**: Identify language versions at a glance
- **Simplified Maintenance**: Directly link corresponding language versions through filenames
- **Native Support**: Works seamlessly with Jekyll without complex configuration

### 2. URL Path Design: Balancing Simplicity and Clarity

Jekyll automatically generates clean URL paths based on file names:
- **Chinese article**: `/yyyy/mm/title.html`
- **English article**: `/yyyy/mm/title_en.html`

This design strikes a perfect balance:
- **Clean URLs**: Maintain simplicity that users and search engines love
- **Clear Identification**: The `_en.html` suffix clearly marks English versions
- **No Extra Configuration**: Works automatically without routing changes

## Technical Implementation Details

### 1. Language Switcher: Elegant Frontend Interaction

The core of seamless language switching lies in JavaScript, which intelligently detects the current page language and generates the URL for the corresponding version. Here's the complete implementation:

```html
{% raw %}
{% if page.url contains '_en.html' %}
  <a href="{{ page.url | replace: '_en.html', '.html' }}" class="language-switcher" id="language-switcher">中文</a>
{% else %}
  <a href="{{ page.url | replace: '.html', '_en.html' }}" class="language-switcher" id="language-switcher">EN</a>
{% endif %}
{% endraw %}

<script>
  // Store language preference in localStorage
  document.addEventListener('DOMContentLoaded', function() {
    var switcher = document.getElementById('language-switcher');
    if (switcher) {
      switcher.addEventListener('click', function(e) {
        var isEnglish = window.location.pathname.endsWith('_en.html');
        localStorage.setItem('preferredLanguage', isEnglish ? 'zh' : 'en');
      });
    }
  });

  // Check for stored preference on page load
  document.addEventListener('DOMContentLoaded', function() {
    var preferredLanguage = localStorage.getItem('preferredLanguage');
    if (preferredLanguage) {
      var isCurrentlyEnglish = window.location.pathname.endsWith('_en.html');
      var shouldBeEnglish = preferredLanguage === 'en';

      // Redirect if current language doesn't match preference
      if (shouldBeEnglish && !isCurrentlyEnglish) {
        var englishUrl = window.location.pathname.replace('.html', '_en.html');
        // Only redirect if the English page actually exists
        fetch(englishUrl, { method: 'HEAD' })
          .then(response => {
            if (response.ok) {
              window.location.href = englishUrl;
            }
          })
          .catch(error => {
            console.error('Error checking English page existence:', error);
          });
      } else if (!shouldBeEnglish && isCurrentlyEnglish) {
        var chineseUrl = window.location.pathname.replace('_en.html', '.html');
        window.location.href = chineseUrl;
      }
    }
  });
</script>
```

### 2. Language Indicators in Page Lists: Smart Tag Display

On category, archive, and tag pages, we need to intelligently display language information. The key principle: **Only show language tags when corresponding language versions exist** to avoid information redundancy.

Here's the implementation logic:

```liquid
{% raw %}
{% if post.url contains '_en.html' %}
  <span class="language-tag en-tag">English</span>
{% else %}
  {% assign en_url = post.url | replace: '.html', '_en.html' %}
  {% for p in site.posts %}
    {% if p.url == en_url %}
      <span class="language-tag zh-tag">中文</span>
      {% break %}
    {% endif %}
  {% endfor %}
{% endif %}
{% endraw %}
```

This implementation offers three key benefits:
- **Smart Display**: Only show language tags when corresponding versions exist
- **Clean Interface**: Avoid unnecessary information redundancy
- **Rigorous Validation**: Verify existence by iterating through all articles

### 3. Language Preference Memory: Enhancing User Experience

To create a smoother experience, we store user language preferences using localStorage. This allows the website to automatically redirect to the user's preferred language version on their next visit:

{% highlight javascript %}
// Store language preference when switching languages
switcher.addEventListener('click', function(e) {
  var isEnglish = window.location.pathname.endsWith('_en.html');
  localStorage.setItem('preferredLanguage', isEnglish ? 'zh' : 'en');
});

// Check for stored preference on page load
var preferredLanguage = localStorage.getItem('preferredLanguage');
if (preferredLanguage) {
  // Redirect logic here
}
{% endhighlight %}

## Content Maintenance Best Practices

### 1. Translation Workflow: Efficient Content Synchronization

After years of maintaining multilingual content, I've developed this efficient workflow:
1. **Write in Chinese First**: Focus on creating complete Chinese content
2. **Create English Copy**: Duplicate the file and add the `_en.md` suffix
3. **Professional Translation**: Translate with attention to context and terminology accuracy
4. **Synchronized Updates**: Always update both versions when making changes

### 2. Keeping Content Synchronized: Practical Tips

- **Synchronization Principle**: Important updates must be applied to all language versions to avoid inconsistency
- **Git Assistance**: Use Git branching and merging to manage multilingual content more effectively
- **Translation Tools**: Leverage tools like DeepL or Google Translate to boost translation efficiency
- **Regular Checks**: Conduct monthly consistency checks to ensure all versions are in sync

### 3. Version Consistency Checks: Automate to Save Time

Manual checks are time-consuming and error-prone. Instead, automate the process with this script:

{% highlight bash %}
# Check for Chinese articles without corresponding English versions
for file in _posts/*.md; do
  if [[ $file != *_en.md && $file != *sample* ]]; then
    english_version="${file%.md}_en.md"
    if [[ ! -f "$english_version" ]]; then
      echo "Missing English version: $english_version"
    fi
  fi
done
{% endhighlight %}

## Common Issues and Solutions

### 1. How to Handle Single-Language Articles?

Our implementation intelligently handles single-language content: language tags are only displayed when corresponding language versions exist. This keeps the interface clean while providing clear information about available translations.

### 2. SEO Optimization for Multilingual Sites: Attract Global Traffic

- **Language Markup**: Correctly tag pages with the `lang` attribute: `<html lang="zh-CN">` or `<html lang="en">`
- **Hreflang Configuration**: Help search engines understand multilingual relationships with proper hreflang tags
- **Content Quality**: Ensure each language version provides independent, valuable content with natural-sounding translation
- **Localization**: Adapt content to regional preferences where appropriate

### 3. Performance Optimization: Smooth User Experience

- **Frontend Switching**: Keep language logic client-side to avoid server redirect delays
- **Preference Caching**: Use localStorage to store preferences and reduce redundant checks
- **Pre-fetching**: Prefetch commonly used language versions to improve switching speed
- **Code Efficiency**: Keep JavaScript lean and avoid blocking page loads

## Comparison with Other Multilingual Solutions: Why Choose the Filename Suffix Scheme?

Let's compare several common multilingual implementation approaches:

### 1. Subdomain Scheme (e.g., en.example.com)
- **Advantages**: Completely separated site structure, ideal for large-scale international sites
- **Disadvantages**: Complex server configuration, cross-subdomain data sharing challenges, high maintenance costs

### 2. Path Prefix Scheme (e.g., example.com/en/)
- **Advantages**: Semantically clear URLs, good for SEO
- **Disadvantages**: Requires Jekyll configuration changes, potentially breaks existing URLs, more complex routing

### 3. Domain Scheme (e.g., example.cn and example.com)
- **Advantages**: Fully independent sites, complete localization potential
- **Disadvantages**: Extremely high maintenance costs, complex cross-site synchronization, domain management overhead

### Why We Chose the File Name Suffix Scheme

Our file suffix approach strikes the perfect balance between simplicity and functionality:
- **Easy Implementation**: Works with Jekyll out of the box
- **Low Maintenance**: Direct file association simplifies updates
- **Cost Effective**: Minimal learning curve and ongoing maintenance
- **Scalable**: Easily extendable to support more languages in the future

This solution is particularly well-suited for personal blogs, portfolios, and small to medium-sized static websites.

## Summary: Multilingual Support Doesn't Have to Be Complex

Implementing multilingual support for static websites can be simple and elegant when you choose the right approach. Our solution is built on four core principles:

1. **Intuitive File Naming**: Use suffixes to clearly identify language versions
2. **Clean URL Design**: Maintain simplicity while indicating language
3. **Seamless Frontend Interaction**: Use JavaScript for smooth language switching
4. **Efficient Maintenance**: Make multilingual content management straightforward

This approach has proven its stability and reliability on my personal blog for years. If you're looking for a practical, low-maintenance way to add multilingual support to your static site, give this method a try!

> "Under the source code, all secrets are revealed." — Hou Jie

---

**Related Reading**:
- [Jekyll Official Documentation](https://jekyllrb.com/docs/)
