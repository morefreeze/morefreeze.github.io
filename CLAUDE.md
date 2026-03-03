# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Jekyll-based personal blog and wiki system called "MoreFreeze's Sanctuary". It's a dual-system architecture with a Jekyll blog and Simiki wiki, focusing on technical articles and algorithm research.

## Common Development Commands

### Blog Development
```bash
# Install dependencies
gem install jekyll jekyll-paginate sass webrick

# Run local development server
jekyll serve --watch
# or
rake preview

# Create a new blog post
rake post title="Your Post Title" [date="YYYY-MM-DD"] [tags="[tag1,tag2]"] [category="category"]

# Create a new page
rake page name="page-name.html"
```

### Wiki Development
```bash
# Generate wiki content
./_gen_wiki.sh

# Preview wiki locally
./_preview_wiki.sh
```

### Testing and Quality Checks
```bash
# Run markdown linting
markdownlint _posts/

# Run spell checking
cspell **/*.md

# Run vale prose linter
vale _posts/
```

## Architecture Overview

### Dual System Architecture

1. **Jekyll Blog System** (`/`)
   - Main blog with posts, categories, tags
   - Theme: Freshman21 (customized)
   - Supports both single and two-column layouts
   - Internationalization support (English/Chinese)

2. **Simiki Wiki System** (`/_wiki/`)
   - Static documentation generator
   - Content in `/_wiki/content/`
   - Output to `/wiki/` directory

3. **Algorithm Code Repository** (`/_code/`)
   - Python implementations of algorithms
   - Test files for verification

### Key Directories

- `_posts/` - Blog posts in Markdown format
- `_includes/` - Reusable Jekyll components
- `_layouts/` - Page layout templates
- `_sass/` - SCSS stylesheets
- `_wiki/content/` - Wiki documentation
- `_code/` - Algorithm implementations
- `assets/` - Static assets (images, CSS, JS)

### Configuration Files

- `_config.yml` - Main Jekyll configuration
- `_wiki/_config.yml` - Wiki configuration
- `Rakefile` - Build automation tasks

### Build and Deployment

The site uses GitHub Actions for CI/CD:
- Automatically builds Jekyll site on push
- Generates wiki content
- Deploys to GitHub Pages
- Build process uses Docker for consistency

### Content Structure

Blog posts use YAML front matter:
```yaml
---
layout: post
title: "Post Title"
description: "Description"
category: algorithm
comments: true
tags: [tag1, tag2]
---
```

Wiki content is organized by topics in `/_wiki/content/` with Markdown files.

### Development Workflow

1. Create or edit content in appropriate directories
2. Test locally with `jekyll serve`
3. Run quality checks (markdownlint, cspell, vale)
4. Commit changes and push to GitHub
5. GitHub Actions automatically builds and deploys

### Important Notes

- The site uses GitHub Pages for hosting (morefreeze.github.io)
- Supports both English and Chinese languages
- Uses MathJax for LaTeX mathematical expressions
- Includes Disqus for blog comments
- Responsive design with mobile support
