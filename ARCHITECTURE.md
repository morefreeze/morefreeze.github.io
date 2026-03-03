# MoreFreeze's Sanctuary - 架构说明文档

## 项目概述

这是一个基于Jekyll的个人博客和Wiki系统，名为"MoreFreeze's Sanctuary"。项目采用双系统架构：主站是基于Jekyll的博客系统，Wiki部分使用Simiki生成静态文档。整体设计简洁优雅，支持中英文双语，专注于技术文章分享和算法研究。

## 技术栈

### 核心技术
- **Jekyll**: 4.x - 静态网站生成器
- **Ruby**: 2.7+ - Jekyll运行环境
- **Simiki**: 1.x - Wiki系统生成器
- **Python**: 3.x - 算法代码和工具脚本
- **GitHub Pages**: 免费托管服务
- **GitHub Actions**: CI/CD自动化部署

### 前端技术
- **HTML5 + CSS3**: 现代Web标准
- **SCSS**: CSS预处理器
- **Bootstrap**: 响应式框架
- **MathJax**: LaTeX数学公式渲染
- **Google Fonts**: Lato和Open Sans字体
- **Font Awesome**: 图标库

### 开发工具
- **Rake**: 任务自动化
- **Vale**: 文本质量检查
- **Markdownlint**: Markdown格式检查
- **CSpell**: 拼写检查

## 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Repository                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌──────────────┐   │
│  │   Jekyll    │    │   Simiki    │    │  Algorithm   │   │
│  │   Blog      │    │    Wiki     │    │    Code      │   │
│  │  System     │    │   System    │    │  Repository  │   │
│  └─────┬───────┘    └─────┬───────┘    └──────┬───────┘   │
│        │                  │                     │           │
│  ┌─────▼───────┐    ┌─────▼───────┐    ┌──────▼──────┐   │
│  │  _config.yml│    │ _config.yml │    │   _code/     │   │
│  │  _layouts/  │    │  content/    │    │  Python算法  │   │
│  │  _includes/ │    │  themes/     │    │   代码库     │   │
│  │  _posts/    │    │  fabfile.py  │    │              │   │
│  │  _sass/     │    │              │    │              │   │
│  └─────┬───────┘    └─────┬───────┘    └──────┬───────┘   │
│        │                  │                     │           │
│  ┌─────▼──────────────────▼─────────────────────▼───────┐   │
│  │              GitHub Actions CI/CD                    │   │
│  │  ┌─────────────┐    ┌─────────────┐                │   │
│  │  │ Jekyll Build │    │ Simiki Build │                │   │
│  │  │   Process    │    │   Process    │                │   │
│  │  └──────┬──────┘    └──────┬──────┘                │   │
│  │         │                  │                       │   │
│  │  ┌──────▼──────────────────▼──────┐                │   │
│  │  │        GitHub Pages Deploy       │                │   │
│  │  │  morefreeze.github.io            │                │   │
│  │  └─────────────────────────────────┘                │   │
│  └───────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 子系统详细架构

#### 1. Jekyll博客系统

**核心配置** (`_config.yml`):
```yaml
# 站点信息配置
site.title: "MoreFreeze's Sanctuary"
site.author: "More Freeze"
site.baseurl: ""
site.absurl: "https://morefreeze.github.io"

# 国际化支持
locales:
  en: { Aboutme: "About Me", Archives: "Archives", ... }
  cn: { Aboutme: "关于我", Archives: "存档", ... }

# 构建配置
markdown: kramdown
highlighter: rouge
plugins: [jekyll-paginate]
paginate: 5
```

**目录结构**:
```
_jekyll/
├── _config.yml          # 主配置文件
├── _layouts/            # 页面布局模板
│   ├── default.html     # 默认布局
│   ├── post.html        # 文章布局
│   └── page.html        # 页面布局
├── _includes/           # 可重用组件
│   ├── head.html        # HTML头部
│   ├── header.html      # 页面头部
│   ├── sidebar.html     # 侧边栏
│   ├── footer.html      # 页脚
│   └── themes/          # 主题组件
├── _posts/              # 博客文章
│   └── YYYY-MM-DD-title.md
├── _sass/               # SCSS样式文件
│   ├── _base.scss       # 基础样式
│   ├── _layout.scss     # 布局样式
│   └── _syntax-highlighting.scss
├── _plugins/            # Jekyll插件
│   └── debug.rb         # 调试插件
└── assets/              # 静态资源
```

**布局系统**:
- **default.html**: 基础布局，包含响应式容器结构
- **post.html**: 文章专用布局，支持评论和标签
- **page.html**: 静态页面布局，简化设计

**响应式设计**:
```scss
// 两列布局 (桌面端)
@media screen and (min-width: 600px) {
  .col-sm-8 { float:left; width:65%; }  // 主内容
  .col-sm-2 { float:right; width:25%; } // 侧边栏
}

// 单列布局 (移动端)
@media screen and (max-width: 600px) {
  .container { width: 100%; }
}
```

#### 2. Simiki Wiki系统

**配置** (`_wiki/_config.yml`):
```yaml
url: 
title: Wiki
root: /wiki
theme: simple
source: content
destination: ../wiki
```

**Wiki结构**:
```
_wiki/
├── _config.yml          # Wiki配置
├── content/             # Wiki内容
│   ├── intro/           # 介绍文档
│   ├── language/        # 编程语言
│   └── unix/            # Unix系统
├── themes/              # Wiki主题
│   ├── simple/          # 简单主题
│   └── simple2/         # 备选主题
└── fabfile.py           # 部署脚本
```

#### 3. 算法代码库

**Python算法实现**:
```
_code/
├── algorithm_c.py       # Algorithm C实现
├── algorithm_c2.py      # Algorithm C优化版
├── sparse_set.py        # 稀疏集合数据结构
├── langford.py          # Langford序列算法
├── codefree.py          # Commafree code生成
└── test_*.py            # 单元测试
```

**核心数据结构**:
- **SparseSet**: 高效的稀疏集合实现
- **Alpha**: 多进制数表示和操作
- **ThreeLines**: 三行链表结构
- **CommaFreeCode**: Commafree code生成器

## 内容架构

### 博客内容分类

**技术文章分类**:
- **algorithm**: 算法研究 (40%)
- **hbase**: 大数据技术 (15%)
- **airflow**: 工作流系统 (10%)
- **beancount**: 财务管理 (10%)
- **game**: 游戏评测 (15%)
- **other**: 其他技术 (10%)

**文章元数据结构**:
```yaml
---
layout: post
title: "文章标题"
description: "文章描述"
category: algorithm
comments: true
tags: [algorithm, knuth, code]
---
```

### Wiki内容组织

**知识库结构**:
- **intro/**: 基础知识介绍
- **language/**: 编程语言指南
- **unix/**: Unix/Linux系统使用

## 部署架构

### CI/CD流程

**GitHub Actions工作流**:
```yaml
name: Jekyll site CI
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v1
    - name: Build the site
      run: |
        docker run \
        -v ${{ github.workspace }}:/srv/jekyll \
        -v ${{ github.workspace }}/_site:/srv/jekyll/_site \
        jekyll/builder:latest /bin/bash -c "chmod 777 /srv/jekyll && jekyll build --future"
```

**部署流程**:
1. 代码推送到GitHub
2. GitHub Actions触发构建
3. Jekyll构建静态网站
4. Simiki构建Wiki文档
5. 自动部署到GitHub Pages

### 开发工具链

**Rake任务系统**:
```ruby
rake post title="新文章标题"    # 创建新文章
rake page name="新页面.html"    # 创建新页面
rake preview                      # 本地预览
rake theme:switch name="主题名"  # 切换主题
```

**Shell脚本工具**:
- **_add_post.sh**: 快速创建文章
- **_gen_wiki.sh**: 生成Wiki文档
- **_preview_wiki.sh**: 预览Wiki

## 性能优化

### 前端优化

**资源优化**:
- SCSS编译为CSS，减少HTTP请求
- 字体图标使用Font Awesome CDN
- 数学公式使用MathJax CDN
- 响应式图片，max-width: 100%

**代码优化**:
```scss
// 使用变量和混合器
$base-font-family: 'Lato', 'Open Sans', Helvetica, Arial, sans-serif;
@mixin media-query($device) {
  @media screen and (max-width: $device) {
    @content;
  }
}
```

### 后端优化

**Jekyll优化**:
- 分页显示，每页5篇文章
- 文章摘要，减少传输数据
- 插件最小化，只保留必要功能

**算法优化**:
- 稀疏集合数据结构，空间换时间
- 回溯算法剪枝，减少搜索空间
- 记忆化技术，避免重复计算

## 安全架构

### 内容安全

**输入验证**:
- Markdownlint检查Markdown格式
- Vale检查文本质量
- CSpell检查拼写错误

**访问控制**:
- GitHub Pages免费托管，公开访问
- 无用户系统，纯静态内容
- 评论系统使用Disqus第三方服务

### 数据备份

**版本控制**:
- 所有内容存储在Git仓库
- GitHub提供完整的版本历史
- 支持回滚到任意历史版本

## 扩展性设计

### 主题系统

**可切换主题**:
- 支持多主题架构
- 主题文件独立管理
- 通过Rake任务快速切换

**国际化支持**:
- 中英文双语支持
- 配置文件式语言管理
- 易于添加新语言

### 插件架构

**Jekyll插件系统**:
```ruby
# 自定义插件示例
module Jekyll
  module DebugFilter
    def debug(obj, stdout=false)
      puts obj.pretty_inspect if stdout
      "<pre>#{obj.class}\n#{obj.pretty_inspect}</pre>"
    end
  end
end
Liquid::Template.register_filter(Jekyll::DebugFilter)
```

## 监控与维护

### 性能监控

**构建监控**:
- GitHub Actions构建状态
- 构建时间监控
- 错误日志记录

**访问监控**:
- Google Analytics集成
- 页面访问统计
- 用户行为分析

### 内容维护

**自动化检查**:
- 链接有效性检查
- 图片完整性验证
- 代码语法高亮

**手动维护**:
- 定期更新依赖
- 内容质量审查
- 性能优化调整

## 总结

MoreFreeze's Sanctuary采用现代化的静态网站架构，具有以下特点：

1. **双系统架构**: Jekyll博客 + Simiki Wiki，功能分离但统一风格
2. **响应式设计**: 支持桌面端和移动端，用户体验一致
3. **算法专注**: 深度算法文章和代码实现，技术含量高
4. **自动化部署**: GitHub Actions实现CI/CD，维护简单
5. **国际化支持**: 中英文双语，面向全球技术社区
6. **性能优化**: 静态生成，CDN加速，访问速度快
7. **可扩展性**: 主题系统、插件架构，易于扩展功能

这个架构既满足了个人技术博客的需求，又提供了完整的知识库系统，是一个优秀的个人技术品牌展示平台。