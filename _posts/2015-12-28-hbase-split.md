---
layout: post
title: "HBase Split"
description: ""
category: tech
tags: [Hadoop, HBase]
---
{% include JB/setup %}

split是什么？
---

HBase的某个或多个region上的文件量达到一定规模，或者人工想拆分，就会进行split，
就是将各个region上的数据拆成两份（一定是一分为二，如果想分成三份就需要进行两次split），
拆分一定是按某个key值，从key这里一切为二，小于key的在前面，大于等于key的在后面。

split有什么用？
---
split的主要作用就是让数据分布更均匀，让每个region都有数据可查，你说这样的决定吼不吼啊，
当然吼啊。举个栗子，在服务上线后，发现总会有些region上的key访问很频繁，而这些key恰好
又都是相近的，那这个region就钦定为热点region(hot region)，这时就需要将这个region
切分下，让这些key分散出去，减少这个region所在的region server的访问。
但要注意的是让HBase自己来决定怎么分可能并没有手动分得好，除非key是完全随机的
（比如md5生成的）。

预split(pre-splitting)
---
预split就是在建表时，指定拆分的各key，可以指定多份，在`HBase shell`下执行就像这样：

`create 'test_table', 'f1', SPLITS=> ['a', 'b', 'c']`

或用外部文件表示，每一行为一个切分点(key)

`$ echo -e  "a\nb\nc" >/tmp/splits`

`create 'test_table', 'f1', SPLITSFILE=>'/tmp/splits'`

自动split
---
如果你之前没听过region还要split也不要紧，HBase会在region量达到一定程度时，自己进行
split。什么时候自动进行split呢，这是根据Split Policy来决定的，0.94之前是一个定值
([ConstantSizeRegionSplitPolicy][1])，之后改成根据一个公式([IncreasingToUpperBoundRegionSplitPolicy][2])
来计算是否要split，这个公式如下：

$$ Min(R^3 * hbase.hregion.memstore.flush.size * 2, hbase.hregion.memstore.flush.size) $$

R是一个表在同一个region server上的region数，`flush.size`为一个配置值，默认为128M，
`file.size`也是配置值，表示超过这个值一定要被split了，默认为10G。

确定要被split了，那哪里是切分点呢，这里要注意的是，切分点只是一个大概的中点，比如：
一个region有key从"000"到"099"，中点应该是"050"（注意我这里故意加了前导的0保持key是等长），
但因为"050"并不一定存在文件的正中，因此HBase取的是[block index][3]的中点(TODO)。

手动split
---
自动split在前面说了并不如自己管理split靠谱（但这也增加了程序员的运维成本），
如果你也下定决心要自己动手，那还需要修改配置文件hbase-site.xml中的
`hbase.hregion.max.filesize`（对，就是前面公式里的第二项）为一个较大的值，比如100G。
因此这里需要说下手动split。只需要在`HBase shell`中执行一条语句：

`split 'regionName', 'splitKey'`

更多用法可以在`HBase shell`中查。另外也可以在HBase的GUI管理界面中直接操作，如果split
point不写，相当于只指定了表要被切分，则HBase会自行将表切分一次。经过几次试验，
这类“自动”切分对于少量数据（比如100条）或没有数据的region不会切分，
每个region都会被测试一次要不要切分。

且听下回
---
你一定想知道split时HBase都做了些什么？

为啥上面的`hbase.hregion.max.filesize`的值设为100G而不是更大甚至无穷大的值？

下篇会继续深入HBase的split操作。

[1]: https://hbase.apache.org/0.94/apidocs/org/apache/hadoop/hbase/regionserver/ConstantSizeRegionSplitPolicy.html "ConstantSizeRegionSplitPolicy"
[2]: https://hbase.apache.org/0.94/apidocs/org/apache/hadoop/hbase/regionserver/IncreasingToUpperBoundRegionSplitPolicy.html "IncreasingToUpperBoundRegionSplitPolicy"
[3]: http://hbase.apache.org/book/apes03.html#d2145e11930 "block index"
