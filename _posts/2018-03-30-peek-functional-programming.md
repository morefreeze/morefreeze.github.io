---
layout: post
title: "初探函数式编程"
description: ""
category: 
comments: true
tags: [functional, python, monad]
---
{% include JB/setup %}

* Table of Contents
{:toc}

最近遇到了一些函数式编程的概念，心想我用 `Python` 的 `map` `reduce` 不就是在函数式编程嘛，
但看了半天仍然一头雾水，什么是 `UnitBox`？`flatMap` 和 `map` 差在哪里？于是先学了阮老师的[函数式编程入门教程][1]，
唉哟喂，和我原来想的还不一样，`Python` 这些操作虽然算是函数式编程，但要系统地理解为什么能这样，
还得从头说起。

<!--more-->
这里我就从阮老师的这篇文章开始，好在他是用 `JS` 讲解的，于是我就写个 `Python` 实现的版本。

### 基本概念

说到函数式编程，肯定都知道“函数是一等公民”这条公理，但这其中少了许多细节。

1. 这个函数只能接受一个参数，并返回一个值
2. 不满足 1 条件的函数可以通过柯里化(curry)来变形成符合 1 条件的
3. 函数之间要满足结合律

翻译成程序员理解的话就是说，函数要没有副作用，比如修改全局变量，传多个参数，
这些都是禁止的。

### 柯里化(curry)

柯里化简单来说就是把接受多个参数的函数通过“俄罗斯套娃”的形式，展成多个函数调用的形式，
每个函数只处理一个函数，就像这样：

```python
def add(x, y):
    return x + y

def curry_add(x):
    return lambda y: x + y

curry_add(2)(3)         # 5
```

显然把好端端的函数都重写一遍挺费劲的，可以用装饰器来简化这一过程，代码受 [pymonad][2] 的启发：

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

上面 `curry` 装饰器直接返回 `wrap` 的调用，而这个 `wrap` 的函数总是返回一个**接受一个参数的函数**的调用，
比如装饰 `add` 函数，第一层返回一个 `add1(x)` 的函数调用，第二层就返回一个 `add2(y)` 的调用，而到第三层，因为 `num_args == 0`，直接调用 `add(x, y)`
将前面的所有参数一起传给 `add`，最终执行 `return x + y`，得到计算结果。

### 函子(Functor)

下面轮到函子出场啦，这是基本的运算单位和功能单位。规定凡是实现了 `map` 方法的都是函子。

听名字有点像函数，但从应用上来看，它表示的是一些我们熟悉的数据类型，比如 `int`, `string` 等，
这些类型可以应用 `map` 操作，比如给一个数翻倍，将一串字符串变成大写。

让我们实现一个简单的函子：

```python
class Functor(object):

    def __init__(self, val):
        self.val = val

    def map(self, f):
        return self.of(f(self.val))

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self.val)

    @classmethod
    def of(cls, *argv, **kwargv):
        return cls(*argv, **kwargv)

Functor.of(2).map(lambda x: x * 2)                          # Functor(4)
Functor.of("foobar").map(lambda x: x.upper)                 # Functor(FOOBAR)
Functor.of(2).map(lambda x: x * 2).map(lambda x: x * 3)     # Functor(12)
```

函子只有一个成员 `val`， 就是用来存储各种数据类型的，然后有一个 `map` 方法，这个方法接受一个函数运算作为参数，将这个函数应用在 `self.val` 上，
但要注意返回的仍然是一个函子，这样后面才能继续应用 `map` 进行操作，
也就是说支持链式操作。

另外 `__repr__` 函数只是为了方便打印调试用的。

注意到还有一个类方法 `of`，这是因为如果直接用 `Functor()` 来初始化不像函数式编程，
所以一般约定使用 `of` 来生成新的对象。

可以看到三个例子展示了`map`操作，注意到第 3 个例子是链式写法，当然这是建立在这些函数都没有副作用的前提下，稍后将会看到这种写法的局限性。

### Maybe 函子

编程中经常遇到一种情况是一个成员初始值赋为 `null` 或 `None`，之后才有可能赋为它的类型的值，
在之后的函数处理中，如果用到这个值，经常会看到 `if (foo == null)` 或 `if foo is None` 的条件语句来做边界处理，
这就比较烦，所以这时要用到 Maybe 函子，它的定义如下：

```python
class Maybe(Functor):

    def map(self, f):
        return self.of(f(self.val) if self.val else None)

Maybe.of('foobar').map(lambda s: s.upper())     # Maybe(FOOBAR)
Maybe.of(None).map(lambda s: s.upper())         # Maybe(None)
```

只是在实现的 `map` 中判断下值是否为空，再根据情况处理即可，其实就是把函数中要进行的判断放到
Maybe 函子中判断了。这个其实很像 `rust` 语言中的 `Option`。

### ap 函子

Functor 只能传数据类型，再应用**接受一个参数**的函数，那对于已经柯里化的多参数函数怎么调用呢，
这时就用到了 ap 函子，ap 是 applicative （应用）的缩写。只要实现 `ap` 方法就行。

```python
class Ap(Functor):

    def ap(self, F):
        return Ap.of(self.val(F.val))
Ap.of(lambda x: x + 2).ap(Maybe.of(2))        # Ap(4)

@curry
def add(x, y):
    return x + y
Ap.of(add).ap(Maybe.of(2)).ap(Maybe.of(3))  # Ap(5)
```

注意到 ap 函子和 Functor（或 Maybe） 的不同是它用**一个函数**（而不是一个数据）初始化，然后将函数应用(apply)在后面的数据上。

### Monad 函子

`Functor.map` 是接受一个普通的函数，这个普通函数接受一个普通值并返回一个普通值，那如果一个函数中可能出现异常导致需要返回一个空值，这时一般我们会让这个函数返回一个封装值，比如这样：

```python
def tryParse(s):
    try:
        return Maybe.of(int(s))
    except ValueError:
        return Maybe.of(None)

Maybe.of('42').map(tryParse)                    # Maybe(Maybe(42))
Maybe.of('foo').map(tryParse)                   # Maybe(Maybe(None))
Maybe.of('42').map(tryParse).map(tryParse)      # TypeError
```

注意到经过 `map` 后的值多套了一层 `Maybe`，这样就没法再用链式写法了，
那怎么办呢，发现 `map` 函数接受的是一个普通值，那么只要让进出一致，就又可以愉快地用链式写法了，
也就是说新 `map` 接受一个封装值并返回一个封装值，里面要做的工作是去掉封装传给真正的处理函数，
我们管这种既能包普通值，又能包函数的类型叫 `Monad`，新 `map` 方法 叫
`flat_map`，这个方法就是把封装的值展开(flat)再应用上 `map`，
就像这样：

```python
class Monad(Fuctor):

    def join(self):
        return self.val

    def flat_map(self, f):
        return self.map(f).join()

def half(x):
    try:
        return Monad.of(x / 2 if x % 2 == 0 else None)
    except TypeError:
        return Monad.of(None)

Monad.of(4).flat_map(half)                  # Monad(2)
Monad.of(3).flat_map(half)                  # Monad(None)
Monad.of(4).flat_map(half).flat_map(half)   # Monad(1)
Monad.of(3).flat_map(half).flat_map(half)   # Monad(None)
```

可以看到给出的后两个例子支持了链式操作，并且如果函数处理得当，对 `None` 值也做了处理。

但如果已经有了一些纯函数，是不是还要都改成返回 `Monad` 的类型呢，
肯定不啦，可以用装饰器轻松达到这个目的，就像这样：

```python
def monadize(f):
    def _(p):
        return Monad.of(f(p))
    return _

@monadize
@curry
def add3(x):
    return x + 3

Monad.of(2).flat_map(add3).flat_map(add3)      # Monad(8)
```

### 小结

这篇文章简单讲了函数式编程的 4 个基础概念：`Functor`, `May`, `Ap` 和 `Monad`，并用 `Python` 简单实现了下。

1. Functor 用来包装数据类型，这里的值可以是数字，字符串，也可以是复杂对象，调用 `map` 方法将函数应用在包装的数据上
1. Maybe 可以将表示空值的 `None` 作为值，并且不会对 `None` 进行操作
1. Ap 可以将多参数的函数包装，调用 `ap()` 不断将参数填充到函数里并求值
1. Monad 使用 `flat_map` 接受一个返回封装值的函数，并将函数的返回值取出，将多层封装展开

### 下期预告

下期将会介绍函数式编程最典型的三种 Monad，有了它们，就可以在函数式编程的海洋里浪了，
所以如果你还没掌握 Monad，可以回头再看一看上面的文章，或者直接在下面留言给我
（也许需要梯子才能加载出留言）。

[1]: http://www.ruanyifeng.com/blog/2017/02/fp-tutorial.html

[2]: https://bitbucket.org/jason_delaat/pymonad/src/cbecd6796cd1488237d2a0f057cefd2a50df753a/pymonad/Reader.py?at=master&fileviewer=file-view-default#Reader.py-91
