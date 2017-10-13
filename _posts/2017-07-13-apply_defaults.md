---
layout: post
title: "airflow apply_defaults 赏析"
description: ""
category: tech
comments: true
tags: [airflow, python, decorator, apply_defaults]
---
{% include JB/setup %}

最近在写 airflow 的脚本时遇到一个问题，出于方便把 `BaseSensorOperator` 包了一层，
后来想改下超时时间和优先级等参数，发现改了没用，于是看了下源码，发现 `Operator` 都有个 `apply_defaults`
的装饰器，细看一看，实现挺巧妙，也解释了我遇到的问题。因为我的问题属于个人使用不当导致的，
所以就不放问题代码了，但我会在分析后给出一些使用方面要注意的地方和建议。

<!--more-->

阅读源码前我假设你已经了解基本的装饰器用法，如果没有，可以看下[这篇文章](http://coolshell.cn/articles/11265.html)。
看的代码是1.8版本的，原文[在这](https://github.com/apache/incubator-airflow/blob/v1-8-stable/airflow/utils/decorators.py)，
这里放一个略带注释的简化版本：

```python
def apply_defaults(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        dag_args = {}  # 这是一个默认参数的字典
        # 这里为了获取dag.default_args，if条件判断能否获取到一个dag实例
        # _CONTEXT_MANAGER_DAG是在使用with语法时获取到dag
        if kwargs.get('dag', None) or airflow.models._CONTEXT_MANAGER_DAG:
            dag = kwargs.get('dag', None) or airflow.models._CONTEXT_MANAGER_DAG
            dag_args = copy(dag.default_args) or {}

        default_args = {}
        # 实际下面一段隐藏了无关内容，所以不要吐槽为啥不用kwargs.get
        if 'default_args' in kwargs:
            default_args = kwargs['default_args']

        dag_args.update(default_args)
        # 至此，default_args包含函数实参default_args和dag.default_args
        default_args = dag_args

        sig = signature(func)
        # 得到这个函数的签名，进而得到必需的参数
        non_optional_args = [
            name for (name, param) in sig.parameters.items()
            if param.default == param.empty and
            param.name != 'self' and
            param.kind not in (param.VAR_POSITIONAL, param.VAR_KEYWORD)]
        # 对于没有明确给出的参数(没有出现在kwargs中)，用default_args来填充
        for arg in sig.parameters:
            if arg in default_args and arg not in kwargs:
                kwargs[arg] = default_args[arg]
        # 如果用default_args填充完还有必需参数没有赋值，则抛出参数缺失异常
        missing_args = list(set(non_optional_args) - set(kwargs))
        if missing_args:
            msg = "Argument {0} is required".format(missing_args)
            raise AirflowException(msg)

        result = func(*args, **kwargs)
        return result
    return wrapper
```

从上面代码我们可以得到参数实际取值顺序：

1. 从对应名字的实参取(`kwargs`)
1. 从`default_args`取
1. 从`dag.default_args`取

有没有发现以上三条似乎少了一条，先别急，来看几个例子，猜猜输出应该是什么。

```python
# coding: utf-8
import datetime
from airflow.utils import apply_defaults
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator

dag_id = 'test_default'
# 这是dag的default_args
default_args = {
    'start_date': datetime.datetime(2017, 7, 13),
    'email': ['morefreeze@gmail.com', ],
    # 注意下面两个参数可能后面会用到
    'priority_weight': 5,
    'bash_command': 'top',
}

dag = DAG(dag_id, default_args=default_args, schedule_interval='@daily')

class DeafOperator(DummyOperator):
    @apply_defaults
    def __init__(self, priority_weight, *args, **kwargs):
        '''这里需要显式给出priority_weight的值'''
        super(DeafOperator, self).__init__(priority_weight=priority_weight,
                                            *args, **kwargs)

class DashOperator(BashOperator):
    @apply_defaults
    def __init__(self, bash_command='ls', *args, **kwargs):
        '''虽然BashOperator需要显式给出bash_command，但这里重载后给个默认值'''
        super(DashOperator, self).__init__(bash_command=bash_command,
                                            *args, **kwargs)

# 给params赋值会影响参数吗？
t1 = DeafOperator(dag=dag, task_id='t1', params={'priority_weight': 1})
print t1.priority_weight
# 给default_args['params']会影响参数吗？
t2 = DeafOperator(dag=dag, task_id='t2', default_args={'params': {'priority_weight': 2}})
print t2.priority_weight
t3 = DeafOperator(dag=dag, task_id='t3', priority_weight=3)
print t3.priority_weight
t4 = DeafOperator(dag=dag, task_id='t4', default_args={'priority_weight': 4})
print t4.priority_weight
# 注意下面是DashOperator的操作，没有给bash_command
t5 = DashOperator(dag=dag, task_id='t5')
# 会输出ls还是top？
print t5.bash_command
```

[答案在这](https://gist.github.com/morefreeze/4e7b1ffe7609527754e57c33cd48872b)

挨个解释下：

1. 根据顺位，没有实参，`default_dags`也没有同名元素，所以取`dag.default_args`。
如果你看源码的话，会看到一大段和`params`相关的处理，但事实上实参取值和`params`一毛钱关系没有
1. 同上
1. 直接用了实参
1. 没有实参，用`default_args`
1. 纳尼？输出是`top`(`dag.default_args`)，你在逗我？这就是我上面说的似乎少了什么东西，按理来说，
如果函数参数有默认值的话，怎么也得让默认值插一脚吧，但源码里确实没有使用默认值的地方，
于是就按顺位取`default_args`（这里是`dag.default_args`），
所以`DashOperator.__init__`的默认值实际是没用的，解决办法是把`dag.default_args['bash_command']`删掉，
或者不要使用`apply_defaults`，也许你并不需要它。

我更倾向于这是一个处理上的 bug，使用参数默认值应当在取不到实参后，取`default_args`前进行，
（也就是顺位1和2之间）这才更符合直觉。

> 源码面前，了无秘密                   —— 侯捷
