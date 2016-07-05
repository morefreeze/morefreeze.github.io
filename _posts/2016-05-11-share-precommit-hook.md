---
layout: post
title: "Share precommit hook"
description: ""
category: tech
comments: true
tags: [git]
---
{% include JB/setup %}

Today I want to share a code snippet. It used for reminding me run `rake preview` before `git commit`.

TL;DR. Because I use `jeklly` to generate my blog static pages, `jeklly` is a generator of static blog.
I can write a markdown file (just like this one) and run `rake preview`, `jeklly` could help me
generate the html files from markdown. So I must remeber run this command before commit changes.
But I often review my articles and found some mistakes in them, I make a tiny hotfix and commit quickly.
In this case, I forgot to re-generate pages. So I made a hook before `git commit` which runs this command
automatically and detects some changes occur. The hook will failed when I forget run the command.

Here it is:

    ./_gen_wiki.sh  # My blog contains a wiki, so it need be generated.
    jekyll build
    git diff --quiet --exit-code _site/  # Detect uncached changes.
    ret=$?
    exec 1>&2
    RED='\033[0;31m'
    NC='\033[0m' # No Color
    [[ x$ret != "x0" ]] && echo "${RED}Some files still not be stage in directory _site${NC}"
    exit $ret

