---
layout: post
title: "airflow 踩坑集锦"
description: ""
category: 
comments: true
tags: [tech, airflow, pit, python]
---
{% include JB/setup %}

距离上一篇[airflow 进阶](/2017/02/airflow-advance.html)居然过了两个月了，
不得不说从上线 airflow 以来问题出了一些，这篇我就来分享下使用过程中踩过的坑，
也欢迎有兴趣的同学发信分享你遇到的问题或者解决办法。
<!--more-->

## celery worker
部到生产环境当然要用 celery 来接任务，再由它进行处理，用 celery 的一个明显好处是 worker 不够的话，
随时加机器扩充 celery 就好，数据的同步放在数据库上处理，简单快捷，而且还有 `/flower` 随时查看worker状况，
在 airflow 自带的看运行任务里，subDAG 的执行是不会显示的，如果开了6个worker，
可能会出现 Task Instance 列表里只有4个任务，但无法 run 新任务，这就是因为有 2 个 subDAG 也有 worker 在跑，
虽然它的作用只是不断轮询等待子任务跑结果。

这也告诉我们，worker不能开得太小，有可能worker里跑得全是subDAG，但实际没有人真正去干活，
这种情况在实践中还没有遇到，但我遇到了另一个类似的情况。

## 饥饿的SensorOperator
操作系统里有种死锁情况叫做“饥饿”(Starve)，如果A需要 R1 资源并产出 R2 资源，B 需要 R2 并产出 R1，
A 和 B一起执行而没人相让的话就会陷入死锁。airflow 也存在这种情况，比如一个任务 A 执行需要检查 B 的状态，
如果任务 A 的 SensorOperator 先启动了，恰好占满了worker，B 就没法启动了，导致 A 会不断轮询 B 的状态，
但都得不到成功的反馈。

解决办法有两种：第一种是把 A 的检测时间设短，更快地失败，加大重试次数，同时调低任务优先级，
这样保证A 和 B都能执行时 B 会先被执行，但如果 B 的执行时间本来就比 A 晚，或者 A 和 B 都是第一次执行，
但不巧 A 先启动而 B 还没启，可能还是会占满worker出现死锁，这个办法治标不治本，
很大程度上降低了死锁的概率，并不能完全避免。

第二种办法比较稳妥，airflow 中有 Pool 的概念，相当于一个队列，可以设置 Pool 的大小，
同一时间只能有这么多任务执行，多的任务排队，可以把 Sensor 相关的任务放在一个 Pool 里，
这样与实际“干活”的任务隔离开，谁都不干扰谁。这种办法治本，只要 worker 数大于 Pool size 就行。
当然我在实际用的时候发现如果有 Pool 的话，使用 SequentialExecutor 会只把任务推到 Pool 里就返回成功了，
测试时可能稍麻烦要把 Pool 注掉。

## depends_on_past 还是 SensorOperator
有时候的脚本需要依赖自己之前产出的一些天的数据，比如计算用户 n 天留存的脚本需要前 n 天的用户访问日志，
一种方法是设置 depends_on_past，如果昨天正常执行了，那说明之前的 n+1天 到前天都正常，
我只要再看昨天日志是否正常就行，但这种有个问题是，如果某一天断了，之后的任务都会中断，
直到有人修复了中断的那天。而且根据[官方的文档](http://pythonhosted.org/airflow/concepts.html?highlight=subdag#subdags)，
不建议在 subDAG 的任务里使用 depends_on_past。
原文是

> refrain from using depends_on_past=True in tasks within the SubDAG as this can be confusing

一般我的做法是使用 ExternalTaskSensor 主动检测依赖的多天任务是否成功，
这样的好处是判断更加清晰，不像 depends_on_past 根本看不出来你具体是依赖几天，
如果中间中断了，在中断了一些天后仍然可以满足条件的情况下启动任务，但我想真发生这种情况也说明这任务并不重要吧。

## 冷启动
这里说的冷启动是指新任务的第一次启动，有一些地方要注意：

1. 任务的 start_date 是否正确，有时候上线时要提个 PR，也许 review 就花了些时间，
最终上线已经距 start_date 好久了，这就要注意是不是真的要重跑这段时间的任务
1. 仍然要再强调一下，如果改了 `schedule_interval` 也一定要改 dag_id，这就相当于新 DAG 了，
记得检查上一条
1. 如果有 SensorOperator 要检查多天（比如一次要检查 7 天）的任务情况，在保证程序正常运行的前提下，
可以将检查天数设为 0，在有足够多的任务时（比如程序已经正常执行了 7 天），再将 SensorOperator 的检查改回 7 天，
这几天只能人工密切关注任务是否成功了，另一个办法是手动人工`Mark success`
1. subDAG 里不提倡有 `depends_on_past`，这可能会导致一些奇怪的问题

## 扩展 Operator
在使用时可以根据具体的需求定制自己的 Operator，比如我们有许多要判断之前**一段** 时间的任务，
如果写一堆 ExternalTaskSensor 就会让图变得比较难看，所以包了下构成了一个 Sensor 可以检测一段时间的类，
依赖一下变得简洁了。

## 目录结构
上一篇说了任务结构一般都在 dags 下建各级目录来区分，但随着业务越来越多，如果只把 python 文件作为 dag_id 名很容易就重了，
而且在新写任务的时候，还要关心新 dag 是否会和别的目录下的 dag 重名，这就很不爽了
（千万别说你们 dag_id 都是手动起的），目前我们采取`{dir}.{file_name}`的形式给 dag 命名，
但缺点是如果目录层数变多，还要写一个比较复杂的函数去取到 dags 根目录位置。

## Jinja2 执行 shell 脚本
上一篇提到了Jinja2在BashOperator里最后要有一个空格来防止错误的转义，这里补充一下，
应该只有在执行 bash 脚本(末尾是.sh扩展名）时才会有这种问题，并不是任何shell命令都有。

## 批量重跑任务
使用airflow的一个主要原因是它有一个可视化的操作界面，但比较不爽的是批量操作只能通过命令行完成，
在前端操作只能**一个一个** clear某个任务让scheduler自动地完成它，而且遇到没有执行过的任务，
还会跳到“核弹页”（出错页面），目前没找到更好的办法。

## Release 1.8
官方在前段时间升级到了 1.8版本，只有[CHANGE_LOG](https://issues.apache.org/jira/secure/ReleaseNote.jspa?projectId=12320023&version=12335682)
功能上没什么大的改进，主要集中在修复 bug 上，前端页面加了更多的信息，
scheduler 显示更易懂的信息。
