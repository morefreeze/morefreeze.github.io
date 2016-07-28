---
title: "Python"
date: 2016-01-18 20:29
---

[TOC][]()

# Network

## Send request with headers

```python
import urllib2

header = {
    'Cookie':       '',
    'Accept':       '',
    'Referer':      '',
    'User-Agent':   '',
}
r = urllib2.Request(url, headers=header)
data = urllib2.urlopen(r).read()
```

See [doc](https://docs.python.org/2/library/urllib2.html)

# Text Processing

## Merge two files with same primary key

```python
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
```

# Algorithm

## Sorting by key

Find more examples [here](https://wiki.python.org/moin/HowTo/Sorting)

```python
student_tuples = [
    ('john', 'A', 15),
    ('jane', 'B', 12),
    ('dave', 'B', 10),
]
sorted(student_tuples, key=lambda student: student[2])   # sort by age
# [('dave', 'B', 10), ('jane', 'B', 12), ('john', 'A', 15)]
```

## Sorting by value

```python
import operator
x = {1: 2, 3: 4, 4: 3, 2: 1, 0: 0}
sorted_x = sorted(x.items(), key=operator.itemgetter(1))
# sorted_x will be a list of tuples. dict(sorted_x) == x
```

# Decorator

## Referer [Python Decorator Library](https://wiki.python.org/moin/PythonDecoratorLibrary)

## @wraps

```python
from functools import wraps
# without @wraps, foo.__name__ will output 'wrapper'
def hello(fn):
    @wraps(fn)
    def wrapper():
        print 'hello, %s' % (fn.__name__)
        fn()
        print 'bye, %s' % (fn.__name__)
    return wrapper

print foo.__name__
```

## Function memo

```python
from functools import wraps
def memo(fn):
    cache = {}
    miss = object()

    @wraps(fn)
    def wrapper(*args):
        result = cache.get(args, miss)
        if result is miss:
            result = fn(*args)
            cache[args] = result
        return result
    return wrapper

@memo
def fib(n):
    if n < 2:
        return n
    return fib(n-2) + fib(n-1)
```

## Profiler

```python
import cProfile, pstats, StringIO

def profiler(fn):
    def wrapper(*args, **kwargs):
        datafn = fn.__name__ + ".profile"
        prof = cProfile.Profile()
        retval = prof.runcall(fn, *args, **kwargs)
        # prof.dump_stats(datafn)
        s = StringIO.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(prof, stream=s).sort_stats(sortby)
        ps.print_stats()
        print s.getvalue()
        return retval
    return wrapper
```

## Time it

```python
# Use for time a function cost time.
# timeit(debug=True), or it will use self._debug if decorate a method of class.
# Usage: @timeit(True)
# class Foo:
#   _debug = True
#   @timeit()
#   def bar(baz):
def timeit(debug=False):
    def real_decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                _debug = debug or args[0]._debug
            except:
                _debug = False
            start_time = time.time()
            retval = fn(*args, **kwargs)
            cost_time = time.time() - start_time
            if _debug:
                print 'function = %s' % (fn.__name__)
                print '    arguments = {0} {1}'.format(args, kwargs)
                print '    cost = %.6f' % (cost_time)
            return retval
        return wrapper
    return real_decorator
```

## Log level

```python
import inspect

def advance_logger(loglevel):

    def get_line_number():
        return inspect.currentframe().f_back.f_back.f_lineno

    def _basic_log(fn, result, *args, **kwargs):
        print "function   = " + fn.__name__,
        print "    arguments = {0} {1}".format(args, kwargs)
        print "    return    = {0}".format(result)

    def info_log_decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            result = fn(*args, **kwargs)
            _basic_log(fn, result, args, kwargs)
        return wrapper

    def debug_log_decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            ts = time.time()
            result = fn(*args, **kwargs)
            te = time.time()
            _basic_log(fn, result, args, kwargs)
            print "    time      = %.6f sec" % (te-ts)
            print "    called_from_line : " + str(get_line_number())
        return wrapper

    if loglevel is "debug":
        return debug_log_decorator
    else:
        return info_log_decorator
```

# Debug

## Measure memory

This snippet is from _Python Cookbook(2nd edition)_ chapter 8.2.
Notich it only work on **Linux**.

```python
import os
import sys
_proc_status = '/proc/%d/status' % os.getpid()
_scale = {'kB': 1024.0, 'mB': 1024.0*1024.0,
          'KB': 1024.0, 'MB': 1024.0*1024.0}
def _VmB(VmKey):
    ''' given a VmKey string, returns a number of bytes. '''
    # get pseudo file  /proc/<pid>/status
    try:
        t = open(_proc_status)
        v = t.read()
        t.close()
    except IOError:
        sys.stderr.write("non-linux?\n")
        return 0.0  # non-Linux?
    # get VmKey line e.g. 'VmRSS:  9999  kB\n ...'
    i = v.index(VmKey)
    v = v[i:].split(None, 3)  # split on runs of whitespace
    if len(v) < 3:
        return 0.0  # invalid format?
    # convert Vm value to bytes
    return float(v[1]) * _scale[v[2]]
def memory(since=0.0):
    ''' Return virtual memory usage in bytes. '''
    return _VmB('VmSize:') - since
def resident(since=0.0):
    ''' Return resident memory usage in bytes. '''
    return _VmB('VmRSS:') - since
def stacksize(since=0.0):
    ''' Return stack size in bytes. '''
    return _VmB('VmStk:') - since
```
