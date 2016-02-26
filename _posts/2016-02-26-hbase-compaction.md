---
layout: post
title: "HBase Compaction"
description: ""
category: tech
tags: [HBase, Hadoop]
---
{% include JB/setup %}

Merge
---

接着上回的[Split](/tech/2015/12/28/hbase-split.html)说，既然有split，那应该对应的有merge吧。然而并没有，也不是完全没有，只是对merge的支持并不像split这么自然，有一些不太稳(kao)定(pu)的工具，可以看[OnlineMerge][1]和[Master initiated automatic region merge][2]。

Compaction
---
下面终于进入正题了，compaction是将一些HStore文件合并或丢弃，从而更高效地去查找。Compaction分两种，一种是Minjor Compaction，另一种是Major Compaction。compaction的触发一般是定期检查文件的状态，如果达到的compaction的条件则进行，而进行compaction无论前面的哪种，都会真刀真枪地去写文件，这就会产生很大的IO，因此这个compaction一般建议设置较大的值，并由外部自行控制一天何时来compaction（比如凌晨没什么业务时）。

Minjor Compaction
---
可以将它理解为一次合并，之后的major compaction相当于多次调用minjor compaction。它的操作是将相邻的两个较小的HStore文件合并，这会将两个文件内容重新写到一个新的位置，并将两个文件删除。如果minjor compaction要合的比较多，就可能会进化成major compaction。

Major Compaction
---
先来看几个参数：

- hbase.hstore.compaction.min 每个Store最少要进行compaction的文件数
- hbase.hstore.compaction.max 每个Store最多要进行compaction的文件数
- hbase.hstore.compaction.min.size HStore小于该值的将被compaction
- hbase.hstore.compaction.max.size HStore大于该值的将被compaction

结合下这几个参数，用人话说的意思就是，major compaction将会选出一些文件，这些文件数在一个范围内，被选出的文件是那些太大或太小（就像果菜摊将坏的或畸形的水果剔除，但在HBase里它们都有用，所以是融合）。

看起来很简单嘛，你想多了，还有一个最重要的参数：

- hbase.store.compaction.ratio compaction的选择系数

这个值的意思对于某个文件，它的大小是a，如果比它小的所有文件大小加起来是b，如果

$$ b * ratio > a $$

那么a将被加进compaction中，否则会按照上面4个参数的限制继续追加。之所以有这个参数应该是防止有一批在范围内的文件（即不胖不瘦），这样总是不会触发compaction，加入这个参数后情况就变了，将会有些文件不得不被compaction，比如第一个文件加入后，后面的文件即使满足条件，但因为有最小文件数的限制，不得不再加入一些。

值得注意的是`ratio`的值越大(>1)，越容易产生较大的文件（因为文件更容易被compaction）。

[1]: https://issues.apache.org/jira/browse/HBASE-7403
[2]: https://issues.apache.org/jira/browse/HBASE-7629
