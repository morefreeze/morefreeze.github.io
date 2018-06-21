---
title: "Shell"
date: 2016-01-20 14:06
---

[TOC][]()

# Text Processing

## awk

### Prepend a newline in a file in the Makefile

- Solution: 

```shell
    @awk BEGIN{print "Header"} {print $0}' foo.txt; \
```

I have tried `sed '1i'` but in Mac it need a newline after `i`, like:

    sed -e '1i\
    Header' foo.txt

But Makefile couldn't input the newline, even if I have read
[this](https://www.gnu.org/software/make/manual/html_node/Splitting-Recipe-Lines.html).
If someone know please let [me](http://morefreeze.github.io/b_about.html) know.

## sed

### tail without last 100 line

Sometime, I may want to see a file last some lines without last some lines(let's say 100).
A direct solution is `wc -l` get the line count then minus 100 use `sed`. But I have seen
a more graceful solution.

- Solution: 

```shell
tac file | sed '1,100d' | tac`
```

## grep

### Only print specified grouping that match

- Background: If there is a file like this:

```
GET /app/path?foo=bar HTTP
```

You need only get the `/app/path?foo=bar HTTP` when `GET` is front of it and
`HTTP` is behind it.

- Solution:

```shell
grep -oP '(?<=GET )[^ ]+(?= HTTP)' file
```

- Explain: `-o` is for only print match, `-P` is for using perl-style regex.
[explainshell](http://explainshell.com/explain?cmd=grep+-oP+%27%28%3F%3C%3DGET+%29%5B%5E+%5D%2B%28%3F%3D+HTTP%29%27)

### Print only appear in left(right) file line

- Background: If your have two files like these:

```
A.csv
1
2
3
5
```

```
B.csv
2
3
4
```

You want to print the line only appear in left(right) file, like this:

```
1
5
```

- Solutions:

```shell
diff --unchanged-line-format= --old-line-format='%L' --new-line-format= A.csv B.csv
```

Or if you need print the line only appear in right file, use this:

```shell
diff --unchanged-line-format= --old-line-format= --new-line-format='%L' A.csv B.csv
```

- Explain: `--LTYPE-line-format=LFMT`

    `LTYPE is 'old', 'new', or 'unchanged'.`
    `%L` is contents of line, other options you can see detail in `man diff`.

## Bash

### Pure bash bible

[https://github.com/dylanaraps/pure-bash-bible]()

### Iterate recursively

- Solutions:

```shell
# Iterate recursively.
shopt -s globstar
for file in ~/Pictures/**/*; do
    printf '%s\n' "$file"
done
shopt -u globstar
```
