---
title: "Python"
date: 2016-01-18 20:29
---

[TOC][]()

# Network

## Send request with headers

    import urllib2

    header = {
        'Cookie':       '',
        'Accept':       '',
        'Referer':      '',
        'User-Agent':   '',
    }
    r = urllib2.Request(url, headers=header)
    data = urllib2.urlopen(r).read()

See [doc](https://docs.python.org/2/library/urllib2.html)

