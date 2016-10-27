---
layout: post
title: "beancount 进阶"
description: ""
category: note
comments: true
tags: [beancount, double-entry]
---
{% include JB/setup %}

{:toc}

## 回顾
[上一篇](/2016/10/beancount-thinking.html)介绍了 beancount 的一般使用方法，以及我个人的记账套路。
但仍然有许多细节没有涉及，这篇文章正是为此而作。
<!--more-->

## 导入账单
这里不得不说一下当初为什么要放弃「随手记」转投了 beancount，正是因为 beancount 它只需要一个文本编辑器就可以记账，
而「随手记」则需要我在手机上或 PC 上指指点点，虽然一套操作也非常流畅，但它并不能**自动化**。
而 beancount 则可以让我以任何方式去记录我的账簿，也使自动解析账单并导入成了可能。

### 真正的导入工作
说到真正的导入工作，不过也就是以下几个步骤：

1. 获取账单，这可能需要模拟登录银行或邮箱页面，然后跳到账单页下载下来，如果直接有下载接口就太方便了
1. 解析账单数据，这通常需要会一些正则和/或 HTML 解析知识，而后者一般可以用 beautilful soup 库去解决
1. 数据再加工，这步用于将上步解析出的数据再加工，按照一定的 beancount 格式去输出，
甚至可以加入一些代码自动去判断部分来源属于哪个账目，比如当收款人是「百度外卖」时，
基本可以确定这是笔「餐饮」消费，当收款人是「中国石油」时，可以确定这是「汽车」上的花费，
随着你记的越来越多，会有越来越多的项目变成固定的一个账目，这又减轻了你的工作
1. 校对，到这步编码工作已经完成，这步是指导入后的校对工作，一般导入时我都会将交易设为未确认("!")，
校对过程也是把"!"改为"\*"的过程

考虑到记账可能会伴随你的一生，花个一下午写个好用的脚本还是值得的，或者到 [github.com]()上搜一下，
有些现成的导入某个银行的账单的脚本。

## 旅行记账
在一生中总会有些大事发生，比如外出旅行，买房装修等等，这时会出现一大笔开销，他会影响你的月平均消费，
因为旅行是一个相对发生更频繁的事，所以这里我举例来说明旅行如何记账。这章的灵感来自于[这里][1]。

### 建立旅行账本
首先是新建一个文本文件，这就是你的旅行账本，这个账本相比主账本会少很多账目，
你可以从主账本里挑一些可能会用到的账目进来，在旅行过程中有可能会根据实际情况添加一些进去。
接着要初始化要用到的账目，比如银行卡，信用卡，如实记录目前的余额。还可能有一些提前兑换的外币也要记录，
有空的话也可以顺便记录下当前的汇率，在之后会有用的。

有一个比较让人纠结的问题是，有时候计划一次旅行，是从很早以前就可以制定的，可能会提前几个月甚至半年，
那么这时候消费记在哪呢。有两种办法，一种办法是这时候就新开账本去记录，这样旅行的花费比较明确。
另一种办法是记在主账本，但加上 tag，这种好处是只需要记一次。我个人建议第二种方法，
虽然这会让这个月的消费有些难看，但我们还是有办法去除掉这个影响的。

### 出发！
首先祝你旅途顺利。然后在每天的晚上回到酒店，可以抽一些时间来回顾下今天的花销，
还是老套路，如果是用的信用卡消费，那可以只简单记个`note`提醒自己有这笔消费，
在账单日导入的时候再实际记上。

如果是花的现金，那就尽量回忆下都花在了哪些地方，
如果不是太累，可以清点下现金对账，因为一天下来可能买了蛋筒，坐了过山车，又吃了大餐，
难免遗漏，没对上的就看情况记在「餐饮」或「娱乐」上吧。

### 合入主账本
这步就像 git 的 merge master 操作了。在旅行结束后回来的某一天，将旅行账本打开，
用工具统计下这次行程的花费，最后可以就「衣食住行」这几大类作下汇总，了解钱都花在哪里。
然后将这几个总数一次写入主账本，并打上个 tag，比如`#trip-some-place-2016`。
在后续的统计中，如果实在不想看到旅行的费用出现在费用中，可以自己写个 SQL 去查询，
比如 `where "#trip-some-place-2016" not in tags` 就行了。

## 建立自己的「梦想」基金
作为一名游戏玩家，时不时需要为信仰充个值，但也不能过度消费，所以我为自己设立了一个「游戏」基金。
买游戏只能使用基金中的钱，如果基金没钱了就不能再买了，这也防止在黑五一些活动中疯狂剁手。

### 账目设立
一个基金需要用到两个账目，一个叫`Expenses:Games:Total`，表示游戏基金的总额，这是个负数，
另一个叫`Expenses:Games:Actual`，表示实际在游戏上花的钱数，这两个其实可以合成一个账目，
但我为了方便追踪我总共花在游戏上的金额，分成了两个账目。

### 增加你的基金
最开始的时候，你的基金肯定为 0，你需要想办法增加你的基金，这样你才有资本去买游戏，
比如你可以每个月在发工资那天，拿出一部分钱充进你的游戏基金，就像下面这样：

```
2016-10-01 * "Games 201610"
            Income:Games                                100 CNY
            Expenses:Games:Total                        -100 CNY
```

你会发现`Expenses:Games:Total`是负的，而`Income`是正的，这和复式记账法有些出入，
但不用纠结那些，这些账目正负并不很重要，你可以理解为现在有一笔未来可能发生的交易入账了，
现在只是为它作了准备。

### Shut up and take my money!
终于可以剁手了，记录交易就变得和正常一样，只是账目变成`Expenses:Games:Actual`，就像这样：

```
2016-10-02 * "Civilization V"
            Liabilities:CMBC:CreditCard                 -23.00 CNY
            Expenses:Games:Actual                       23.00 CNY
```

可以看出我在第二天趁打折入了《下一回合 V》。现在检查下基金状况，-100+23=-77，
也就是说我还有 77 块可以用来买入游戏，这你也可以直接统计`Expenses:Games`来获得。

### 小遗憾
这种办法唯一的小遗憾是和账单导入的配合上，因为账单导入总是延迟记录已经发生的一切，
所以我有可能这个月已经买了许多游戏却无法实时地反映在「游戏」基金上，我只能自己手动记录已经买的游戏价格，
再与总数相减。所以最终我决定不管它了，我会对我的当前基金健康状况有个把握，
即使在账单日发现真的超出了预算也没关系，只能在下个月回血让它再度正常了，而我超额的越多，
需要恢复的时间就越长，也就提醒我一定要理智消费，毕竟设立这个基金的目的也是为了控制消费欲望。

## Query
我多次强调记账的目的是为了分析自己的财条状况，而之前提到的 fava 或者 beancount 原生的页面已经能很好的展示一些报表了。
但对于一些特殊需求就需要手写 SQL 来解决了，比如上面在「旅行记账」一章里提到过滤掉tag。

beancount 的 SQL 与 MySQL 等的语法比较，只要搞清楚实际会有哪些列以及一些函数就行了，具体语法可以参考[这里][2]。

首先是常用的几个 columns：

|名称   |意义    |示例  |
|date   |表示日期|2016-01-01|
|narration  |详情   |But something|
|payee      |收款人 |somebody   |
|position   |金额   |12.34 CNY  |
|tags       |tag 集合，是一个list   |trip-some-place-2016|

### 例子

- 统计当月的`Expenses`和`Income`，最后只列出支出和收入加和各是多少

```
SELECT
    year, month, root(account, 1) as account, sum(position) as total
FROM
    year = YEAR(today()) and month = MONTH(today())
WHERE
    account ~ 'Expenses' OR
    account ~ 'Income'
GROUP BY year, month, account
ORDER BY year, month, account
FLATTEN
```

- 统计当月具体支出项

```
SELECT
    account, sum(cost(position)) as total, month
FROM
     year = YEAR(today()) and month = MONTH(today())
WHERE
    account ~ 'Expenses:*'
GROUP BY month, account
ORDER BY total, account DESC
```

更多的例子可以查看[这里][3]。


## 其它
最后还有些其它零碎相关的东西要扯一扯。

### 备份
这个我折腾了好久，后来采取定时同步到云盘 + git 的方法管理，同步云盘简单粗暴，
但现在这个环境下不知道哪天哪个盘又倒了，所以还是找个靠谱的国外云盘吧。git 可以同步一些配套的脚本，
但账本属于比较隐私的东西，就不适合放在 github 了，开个 private repo 又不值当，
这种可以自己搞个 gitlab 或者国内的类似产品。

### 运行在云上
之前在网上找教程时找到了[这篇][4]，其中介绍了如何将 fava 部署在 [pythonanywhere](https://www.pythonanywhere.com/) 上，
喜欢折腾的可以自己按教程撸一遍，我之前也是在上面部署成功的。

[1]: https://docs.google.com/document/d/1FRcJqUfeAMQO6KjG94w6rF7VajMGJaFplmF1Wu0rCHY/edit   "Sharing Expenses in Beancount"
[2]: https://docs.google.com/document/d/1s0GOZMcrKKCLlP29MD7kHO4L88evrwWdIO0p4EwRBE0/edit   "Beancount Query Language"
[3]: https://aumayr.github.io/beancount-sql-queries/    "SQL queries"
[4]: https://alexjj.com/blog/2016/2/managing-my-personal-finances-with-beancount/   "Managing my personal finances with beancount"
