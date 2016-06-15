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

# Text Processing

## Merge two files with same primary key

    # coding: utf-8

    import csv
    import os
    import sys

    __doc__ = '''
    python %s left_file left_idx right_file [right_idx]
    It will join right_file to left_file on(left.idx=right.idx).
    The columns of right_file will be paste after left_file.
    The index of both must be unique and start with 0.
    e.g.:    left     |     right
          1 A B C     |   1 X Y
          2 D E F     |   3 Z W
          3 H I J     |   (EOF)
    result is:
                  merged
          1 A B C X Y
          2 D E F
          3 H I J Z W
    ''' % (sys.argv[0])


    def generate_outfile(f1, f2):
        return os.path.splitext(f1)[0]+'_ext.csv'

    if __name__ != '__main__':
        exit(0)

    if len(sys.argv) <= 3:
        print "Usage: python %s left_file left_idx right_file [right_idx]" \
            % (sys.argv[0])
    # d[left_idx] = left_row
    d = {}
    left_file = str(sys.argv[1])
    left_idx = int(sys.argv[2])
    right_file = str(sys.argv[3])
    right_idx = 0 if len(sys.argv) > 3 else int(sys.argv[4])
    with open(right_file, "rb") as f:
        r = csv.reader(f)
        for row in r:
            if len(row) <= right_idx:
                continue
            new_row = row[:right_idx] + row[right_idx+1:]  # Remove right_idx.
            d[row[right_idx]] = new_row

    out_file = generate_outfile(left_file, right_file)
    with open(out_file, "wb") as out_f:
        w = csv.writer(out_f)
        with open(left_file, "rb") as f:
            r = csv.reader(f)
            for row in r:
                if len(row) > left_idx and row[left_idx] in d:
                    row += d[row[left_idx]]
                w.writerow(row)

# Algorithm

## Sorting by key

Find more examples [here](https://wiki.python.org/moin/HowTo/Sorting)

    student_tuples = [
        ('john', 'A', 15),
        ('jane', 'B', 12),
        ('dave', 'B', 10),
    ]
    sorted(student_tuples, key=lambda student: student[2])   # sort by age]
    # [('dave', 'B', 10), ('jane', 'B', 12), ('john', 'A', 15)]
