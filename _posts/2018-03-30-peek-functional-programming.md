---
layout: post
title: "初探函数式编程"
description: ""
category: 
comments: true
tags: [functional, python, monad]
---
{% include JB/setup %}

最近遇到了一些函数式编程的概念，心想我用 python 的 `map` `reduce` 不就是在函数式编程嘛，
但为什么我却看不懂呢，于是先学了阮老师的[函数式编程入门教程](http://www.ruanyifeng.com/blog/2017/02/fp-tutorial.html)，
唉哟喂，和我原来想的还不一样，python 这些操作算是函数式编程，但要系统地理解为什么能这样，
还得从头说起。

<!--more-->
这里我就从阮老师的这篇文章开始，好在他是用 JS 讲解的，于是我就写个 python 实现的版本。

### 基本概念

说到函数式编程，肯定都知道“函数是一等公民”这条公理，但这其中少了许多细节。

1. 这个函数只能接受一个参数，并返回一个值
2. 不满足 1 条件的函数可以通过柯里化(curry)来变形成符合 1 条件的
3. 函数之间要满足结合律

翻译成程序员理解的话就是说，函数要没有副作用，比如修改全局变量，传多个参数，
这些全是禁止的。

### 柯里化 curry

柯里化简单来说就是把多个参数的函数参过“俄罗斯套娃”的形式，展成多个函数调用的形式，
每个函数只处理一个函数，就像这样：

```python
def add(x, y):
    return x + y

def curry_add(x):
    return lambda y: x + y

curry_add(2)(3)         # 5
```

显然把好端端的函数重写一遍挺费劲的，可以用装饰器来简化这一过程，代码受 [pymonad][1] 的启发：

```python
def curry(f):
    num_args = f.__code__.co_argcount
    def wrap(args, num_args):
        if num_args == 0:
            return f(*args)
        # 每次返回一个只接受一个参数的函数
        return lambda x: wrap(args + [x], num_args - 1)
    return wrap([], num_args)

@curry
def add(x, y):
    return x + y

add(2)(3)       # 5
```


对比了中外的几篇文章，我发现函数式编程的概念的讲解顺序出入挺大的，不过一般学习都会从 Haskell
开始，从语言中慢慢理解函数式编程的关键概念，

[1]: https://bitbucket.org/jason_delaat/pymonad/src/cbecd6796cd1488237d2a0f057cefd2a50df753a/pymonad/Reader.py?at=master&fileviewer=file-view-default#Reader.py-91