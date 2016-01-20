---
title: "Shell"
date: 2016-01-20 14:06
---

[TOC][]()

### Prepend a newline in a file in the Makefile

- Solution: `@awk BEGIN{print "Header"} {print $0}' foo.txt; \ `

I have tried `sed '1i'` but in Mac it need a newline after `i`, like:

``shell
sed -e '1i\
Header' foo.txt
``

But Makefile couldn't input the newline, even if I have read 
[this](https://www.gnu.org/software/make/manual/html_node/Splitting-Recipe-Lines.html)

