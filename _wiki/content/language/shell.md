---
title: "Shell"
date: 2016-01-20 14:06
---

[TOC][]()

# Text Processing

## awk

### Prepend a newline in a file in the Makefile

- Solution: `@awk BEGIN{print "Header"} {print $0}' foo.txt; \ `

I have tried `sed '1i'` but in Mac it need a newline after `i`, like:

    sed -e '1i\
    Header' foo.txt

But Makefile couldn't input the newline, even if I have read
[this](https://www.gnu.org/software/make/manual/html_node/Splitting-Recipe-Lines.html).
If someone know please let [me](http://morefreeze.github.io/b_about.html) know.

## sed

## grep

### Only print specified grouping that match

- Background: If there is a file like this:

    GET /app/path?foo=bar

You need only get the `/app/path?foo=bar HTTP` when `GET` is front of it and
`HTTP` is behind it.

- Solution: `grep -oP '(?<=GET )[^ ]+(?= HTTP)' file`

- Explain: `-o` is for only print match, `-P` is for using perl-style regex.
[explainshell](http://explainshell.com/explain?cmd=grep+-oP+%27%28%3F%3C%3DGET+%29%5B%5E+%5D%2B%28%3F%3D+HTTP%29%27)
