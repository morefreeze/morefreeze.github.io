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
随时加机器扩充 celery 就好，数据的同步放在数据库上处理，简单快捷，而且还有/flower随时查看worker状况，
在airflow自带的看运行任务里，subdag的执行是不会显示的，如果开了6个worker，
可能会出现Task Instance 列表里只有4个任务，但无法run新任务，这就是因为有2个subdag也是worker在跑，
虽然它的作用只是不断轮询等待子任务跑结果。

这也告诉我们，worker不能开得太小，有可能worker里跑得全是subdag，但实际没有人真正去干活，
这种情况在实践中还没有遇到，但我遇到了另一个类似的情况。

## 饥饿的SensorOperator
操作系统里有个死锁情况叫做“饥饿”(Starve)，如果A需要R1资源并产出R2资源，B需要R2并产出R1，
A B一起执行没人相让的话就会陷入死锁。airflow 也存在这种情况，比如一个任务A执行需要检查B的状态，
如果任务A的SensorOperator先启动了，恰好占满了worker，B就没法启动了，导致A会不断轮询B的状态，
但都得不到成功的反馈。

解决办法有两种：第一种是把A的检测时间设短，更快地失败，加大重试次数，同时调低任务优先级，
这样保证A B都能执行时B会先被执行，但如果B的执行时间本来就比A晚，可能还是会占满worker出现死锁，
这个办法治标不治本，很大程度上降低了死锁的概率，并不能完全避免。

第二种办法比较稳妥，airflow中有Pool的概念，相当于一个滑动窗口，可以设置Pool的大小，
同一时间只能有这么多任务执行，多的任务在队列里，可以把Sensor相关的任务放在一个Pool里，
这样与实际“干活”的任务隔离开，谁都不干扰谁。这种办法治本，只要worker数大于Pool size就行。
当然我在实际用的时候发现如果有Pool的话，使用SequentialExecutor会只把任务推到Pool里就返回成功了，
测试时可能稍麻烦要把Pool注掉。

## 目录结构
上一篇说了任务结构一般都在dags下建各级目录来区分，但随着业务越来越多，如果只把python文件作为dag_id名很容易就重了，
而且在新写任务的时候，还要关心新dag是否会和别的目录下的dag重名，这就很不爽了
（千万别说你们dag_id都是手动起的），目前我们采取'{dir}.{file_name}'的形式给dag命名，
但缺点是如果目录层数变多，还要写一个比较复杂的函数去取到dag根目录位置。

## Jinja2 执行 shell 脚本
上一篇提到了Jinja2在BashOperator里最后要有一个空格来防止错误的转义，这里补充一下，
应该只有在执行 bash 脚本(末尾是.sh扩展名）时才会有这种问题，并不是任何shell命令都有。

## 批量重跑任务
使用airflow的一个主要原因是它有一个可视化的操作界面，但比较不爽的是批量操作只能通过命令行完成，
在前端操作只能**一个一个** clear某个任务让scheduler自动地完成它，而且遇到没有执行过的任务，
还会跳到“核弹页”（出错页面），目前没找到更好的办法。

## Release 1.8
官方在前段时间升级到了 1.8版本，只有[CHANGE_LOG](https://issues.apache.org/jira/secure/ReleaseNote.jspa?projectId=12320023&version=12335682)
功能上没什么大的改进，主要集中在修复 bug 上，前端页面加了更多的信息，但使用起来还是会遇到之前的一些问题。
