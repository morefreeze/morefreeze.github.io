---
layout: post
title: "airflow priority_weight 计算方法"
description: ""
category: 
comments: true
tags: [airflow, python]
---
{% include JB/setup %}

最近发现 airflow 任务执行顺序有些奇怪，于是看了下 airflow 关于权重的处理，解答了心中的疑问。

以最新的稳定版(v1.8-stable)为例，代码总共就这么[一小段](https://github.com/apache/incubator-airflow/blob/v1-8-stable/airflow/models.py#L2161-L2166)

```python
    @property
    def priority_weight_total(self):
        return sum([
            t.priority_weight
            for t in self.get_flat_relatives(upstream=False)
        ]) + self.priority_weight
```

<!--more-->

这是类 Operator 下的一个属性，同时可以发现在 airflow 里，Task 和 Operator 概念是互通的，
（可以看到许多地方传参都是一个 task，实际传的都是 Operator。注意区别 Task 和 TaskInstance）
计算方法就是把所有下游（依赖它的）任务的权重和自己的权重加起来，`get_flat_relatives`
就是递归地遍历所有下游任务，返回一个数组，顺便说下`upstream=True`就是遍历所有上游任务。

因此，可以得到一个结论，任务依赖层级越多，越容易出现权重大的任务，这也就解释了为什么我设置了
`t1 >> t2`权重都是7，又设置了`r1 >> r2 >> r3` 权重都是5，`t1`的权重却比`r1`的权重小。

> 源码面前，了无秘密                   —— 侯捷
