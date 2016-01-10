---
layout: post
title: "HBase Split detail"
description: ""
category: tech
tags: [Hadoop, HBase]
---
{% include JB/setup %}

split的具体过程
---
切分的操作是由各个region server自己决定，但它们要通知到Master来及时地更新META信息。
以下基本翻译自[这里][1]。

1. region server决定开始split，在zk上创建新节点`/hbase/region-in-transition/parent-region-name:SPLITTING`
1. Master通过监测这个节点得知父region（这时称要split的region为父，
分出来的新的region为女儿region）要split了
1. region server在HDFS目录下创建一个子目录`.splits`，如`.../parent-region-name/.splits`
1. region server关闭父region，这时所有到父region的请求都会返回`NotServingRegionException`的异常，
需要客户端自己进行重试
1. 在刚才创建的`.splits`目录下，创建两个女儿目录的引用，如
`.../parent-region-name/.splits/daughterA`和`.../parent-region-name/.splits/daughterB`，
其中文件都引用自父region，引用文件标记出开始和结束位置
1. region server在HDFS中创建实际的女儿region目录，如`.../daughterA/`，再将刚才创建的
引用文件移到这个目录中
1. region server发送一个PUT请求给META信息表，加入女儿region信息，并将父region下线。
注意这时client扫描META表并不能发现新的region，因为还没上线。
如果这个RPC请求失败了，那么Master和下一个要执行打开region的region server一起清理掉
这些脏数据
1. region server允许女儿region的写入
1. region server将女儿信息在META中上线，客户端这时可以发现新的region。注意将缓存的
region信息重新更新
1. 将zk中的节点，改为`/hbase/region-in-transition/parent-region-name:SPLIT`，这样
Master就知道split完成
1. 现在，HDFS中存的仍然是女儿region到父region的引用，要等compaction操作去将引用
的数据重写到新文件，当新文件都重写完后，才会完全删掉父region

且听下回
---
下回将会详细介绍辛勤劳动的compaction操作。

[1]: http://hortonworks.com/blog/apache-hbase-region-splitting-and-merging/
