---
layout: post
title: "博客搬家：从 GitHub Pages 到自定义域名"
description: "记录博客迁移到 blog.morefreeze.top 的过程和思考"
category: life
comments: true
tags: [博客, 域名, GitHub Pages, DNS]
---

最近做了一件拖了很久的事情——给博客换了个域名。新地址是 **blog.morefreeze.top**，旧的 `morefreeze.github.io` 会自动跳转过来，不影响之前收藏的链接。

<!--more-->

## 为什么要换

用了好几年 `morefreeze.github.io`，其实一直没什么不满。GitHub Pages 免费、稳定、部署方便，对个人博客来说绰绰有余。

但说实话，换域名这件事没什么深思熟虑——`.top` 域名一年几块钱，某天刷到续费提醒，顺手就买了。买都买了，不用也浪费。

真要说理由的话，大概就是**拥有感**。`github.io` 后缀终究是别人家的地盘，哪天 GitHub 改策略了，连个跳转都不一定给你留。有个自己的域名，至少迁移的时候 DNS 一改就行，不用求人。

## 迁移过程

整个过程比想象中简单，主要就三步：

### 1. 买域名

在域名注册商买了 `morefreeze.top`，然后配置 DNS 解析，添加一条 CNAME 记录：

```
blog.morefreeze.top  →  morefreeze.github.io
```

### 2. 配置 GitHub Pages

在仓库根目录创建 `CNAME` 文件，内容就一行：

```
blog.morefreeze.top
```

然后在 GitHub 仓库的 Settings → Pages 里确认 Custom domain 已经生效，顺便勾上 Enforce HTTPS。

### 3. 更新站点配置

把 `_config.yml` 里的 `url` 改成新域名：

```yaml
url: "https://blog.morefreeze.top"
```

推送后等 DNS 生效（通常几分钟到几小时），就搞定了。

## 注意事项

迁移过程中有几个值得注意的点：

- **旧链接不会失效**。GitHub Pages 默认会把 `morefreeze.github.io` 的请求 301 到自定义域名，所以之前被搜索引擎收录的页面、别人分享的链接都不会变成死链。
- **HTTPS 证书**。GitHub Pages 会自动为自定义域名申请 Let's Encrypt 证书，不需要自己折腾。
- **RSS 订阅**。如果有人通过 RSS 订阅了博客，feed 地址会变，但大部分 RSS 阅读器能自动跟随跳转。

## 最后

域名这件事，早做早省心。拖了这么久，实际操作不到半小时就搞定了。如果你也在用 GitHub Pages 写博客，强烈建议花几块钱买个自己的域名——毕竟在互联网上，域名就是你的门牌号。

新地址：[blog.morefreeze.top](https://blog.morefreeze.top)

欢迎更新书签 :)
