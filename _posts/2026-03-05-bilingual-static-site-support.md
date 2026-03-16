---
layout: post
title: "静态网站多语言支持最佳实践 - 以中英双语为例"
description: "分享在Jekyll静态网站中实现中英双语支持的技术细节和最佳实践"
category: fe
comments: true
tags: [devops, jekyll, static-site, bilingual, i18n]
---
{% include JB/setup %}


{:float-toc}

## 前言

想象一下，你的一篇技术文章被外国开发者看到，但因为语言障碍，他们无法理解其中的精髓。或者一位国际读者想了解你的观点，却因为语言问题而放弃。在全球化的今天，多语言支持已经不再是加分项，而是必备功能。

但是，很多静态网站的多语言实现要么过于复杂，要么不够优雅。今天，我想结合我的个人博客实现，分享一种简单、直观且易于维护的方案，带你在Jekyll静态网站中优雅地实现中英双语支持。

## 核心实现思路

### 1. 文件命名规范：用文件名直接标识语言

我采用了一种非常直接且易于理解的文件命名方式：
- 中文文章：`yyyy-mm-dd-title.md`
- 英文文章：`yyyy-mm-dd-title_en.md`

这种命名方式的三大优点：
<!--more-->
- **直观易懂**：一眼就能区分文章的语言版本
- **便于维护**：对应语言版本的文章通过文件名直接关联
- **原生支持**：Jekyll能够自动识别并正确生成对应的URL路径

### 2. URL路径设计：保持简洁与清晰的平衡

Jekyll会根据文件名自动生成干净的URL路径：
- 中文文章URL：`/yyyy/mm/title.html`
- 英文文章URL：`/yyyy/mm/title_en.html`

这种设计巧妙地在简洁性和清晰度之间找到了平衡：
- URL结构保持简洁，符合用户习惯
- 通过`_en.html`后缀清晰地标识英文版本
- 不需要复杂的路由配置或重定向规则

## 技术实现细节

### 1. 语言切换器：优雅的前端交互

实现无缝语言切换的核心是JavaScript，它能够智能检测当前页面语言并生成对应语言版本的URL。下面是完整的实现：

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

### 2. 页面列表中的语言标识：智能显示语言标签

在分类、归档和标签等文章列表页面，我们需要智能地显示文章的语言信息。关键在于：**只有当文章存在对应语言版本时才显示标签**，避免信息冗余。

实现逻辑如下：

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

这种实现方式的三大优点：
- **智能显示**：只有当文章存在对应语言版本时才显示标签
- **界面简洁**：避免了不必要的信息冗余
- **逻辑严谨**：通过遍历所有文章验证对应版本是否存在

### 3. 语言偏好记忆：提升用户体验的小细节

为了让访问体验更加流畅，我们可以通过localStorage存储用户的语言偏好。这样用户下次访问时，网站会自动跳转到他们偏好的语言版本：

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

## 内容维护最佳实践

### 1. 翻译工作流：高效保持内容同步

我经过多次实践，总结出这套高效的翻译工作流：
1. **先完成中文创作**：集中精力完成中文文章的写作
2. **创建英文副本**：复制一份并重命名为`_en.md`后缀的文件
3. **专注英文翻译**：进行专业的英文翻译，注意语境和术语准确性
4. **同步更新内容**：如果需要修改，务必同时更新两个版本的内容

### 2. 保持内容同步：实用技巧分享

- **同步更新原则**：重要更新应该同步到所有语言版本，避免内容不一致
- **Git辅助管理**：可以使用Git的分支和合并功能辅助管理多语言内容
- **翻译工具助力**：考虑使用翻译记忆工具（如DeepL、Google Translate）提高翻译效率
- **定期检查**：每月至少检查一次多语言版本的一致性

### 3. 版本一致性检查：自动化脚本解放双手

手动检查多语言版本一致性非常耗时，我们可以通过脚本来自动化这个过程：

{% highlight bash %}
# 检查是否有中文文章没有对应的英文版本
for file in _posts/*.md; do
  if [[ $file != *_en.md && $file != *sample* ]]; then
    english_version="${file%.md}_en.md"
    if [[ ! -f "$english_version" ]]; then
      echo "Missing English version: $english_version"
    fi
  fi
done
{% endhighlight %}

## 常见问题与解决方案

### 1. 如何处理只有单语言的文章？

对于只有单语言的文章，我们的实现逻辑会智能判断——只有当对应语言版本存在时，才会显示语言标签。这样既保持了界面简洁，又避免了不必要的提示。

### 2. 多语言站点的SEO优化：吸引全球流量

- **语言标记**：使用`lang`属性正确标记页面语言：`<html lang="zh-CN">`或`<html lang="en">`
- **hreflang配置**：配置hreflang标签帮助搜索引擎理解多语言内容关系
- **内容质量**：确保每个语言版本的内容是独立且有价值的，避免机器翻译痕迹过重
- **本地化优化**：针对不同语言区域的用户习惯进行内容微调

### 3. 性能优化：流畅的用户体验

- **前端切换**：语言切换逻辑放在前端，避免服务器端重定向的延迟
- **偏好缓存**：使用localStorage缓存语言偏好，减少不必要的检查
- **预获取优化**：预获取常用语言版本的页面，提高切换速度
- **代码精简**：确保JavaScript代码精简高效，避免阻塞页面加载

## 对比其他多语言方案：为什么选择文件名后缀？

让我们来对比几种常见的多语言实现方案：

### 1. 子域名方案（如 en.example.com）
- 优点：完全分离的站点结构，适合大型网站
- 缺点：配置复杂，跨子域名共享数据困难，维护成本高

### 2. 路径前缀方案（如 example.com/en/）
- 优点：URL结构清晰，语义化程度高
- 缺点：需要修改Jekyll配置，增加复杂度，可能影响现有URL结构

### 3. 域名方案（如 example.cn 和 example.com）
- 优点：完全独立的站点，适合需要本地化深度定制的场景
- 缺点：维护成本极高，跨站内容同步困难

### 我们的选择：文件名后缀方案

我们选择的文件名后缀方案在实现复杂度和维护便捷性之间找到了完美的平衡：
- **实现简单**：不需要复杂的配置，Jekyll原生支持
- **维护便捷**：通过文件名直接关联对应语言版本
- **成本低廉**：学习成本和维护成本都很低
- **扩展性好**：可以很容易地扩展到更多语言版本

这种方案特别适合个人博客和中小型静态网站。

## 总结：多语言支持其实可以很简单

实现静态网站的多语言支持并不复杂，关键在于找到一种简单、直观且易于维护的方案。我们的方案核心在于四个要点：

1. **简单的文件命名规范**：通过文件名后缀区分语言版本
2. **清晰的URL设计**：保持URL简洁同时清晰标识语言
3. **优雅的前端交互**：使用JavaScript实现无缝的语言切换
4. **便捷的内容维护**：让作者能够轻松管理多语言版本

这种方案已经在我的个人博客稳定运行多年，证明了它的有效性和可靠性。如果你也在为静态网站的多语言支持发愁，不妨试试这种简单而优雅的方案！

> 源码面前，了无秘密 —— 侯捷

---

**相关阅读**：
- [Jekyll官方文档](https://jekyllrb.com/docs/)
