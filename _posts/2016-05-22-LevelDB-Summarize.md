---
layout: post
title: "LevelDB实现总结"
description: "一个关于LevelDB实现的简短总结"
category: tech
tags: [algorithm, database]
---
{% include JB/setup %}

学习了下LevelDB的实现原理，发现G厂大神Jeff Dean果然牛B，实现也很巧妙。
参考链接是[这里](http://www.cnblogs.com/haippy/archive/2011/12/04/2276064.html)

## 概览
1. LevelDB是一个KV**持久化**存储引擎，它的特性是写非常快，读相对写较慢
1. LevelDB是基于LSM(Log Structured Merge)实现，它是顺序地记录各种写操作
1. LevelDB存储分为两部分，一部分记成内存中方便快速查找，查找失败后，去另一部分的
磁盘上查找。一段时间后或内存达到一定大小，会将内存中的compact成sst文件存在磁盘

## 内存存储
1. 内存存储叫memTable，存储结构为跳表，存储为顺序存储，查找和写入都很快(O(log N))
1. 删除操作在这里只是打上删除标记，真正的删除在compaction中做的

## 日志
1. 日志文件记录了每一步的操作，因为文件的append操作很快，所以这是为什么LevelDB
写操作快的原因
1. 每次的写都会先在日志上记一笔，记完后去更新memTable
1. 如果重启等情况，LevelDB就会将已经持久化的文件与日志进行一个merge操作，这就是LSM，
与HBase的恢复操作很相似

## 磁盘存储
1. 磁盘存储叫immuteTable，以一种分层的结构存储，层数从0到n（n会随着数据增多而增多），
层数越高表示数据越老旧（可能存在相同的key），除了**层0**，其他层之间的key都是不相交的
1. 查找的顺序从这里已经可以得出来了memTable->层0->层1->...->层n，这也是LevelDB名字的由来，
那么数据是如何从**memTable到层0**呢
1. 层数0是将memTable整个dump出来的结果，因此可能之间有相交，这个操作叫**minor compaction**
1. major compaction是将层i合到i+1中去，合并是将层i中的一块合到整个层i+1中去，
这个过程类似归并排序，将参与的几个块全部取出来排序，再重新组合成新的层i+1，同时
会将重复的key**弃掉**
1. 弃掉是指如果key已经出现在更低的层，则高级的层不需要记录这个key

## 文件格式
1. 实际硬盘存储并非只有一种sst文件，分为三种：
  1. sst文件记录实际的数据，按顺序排列
  1. manifest文件是sst文件的索引表，记录各个层0文件的key range
  1. current文件记录当前的manifest文件是哪个
1. **sst文件**存储的格式像这样：key共享长度，key非共享长度，value长度，key非共享内容，
value 内容。共享长度指的是相邻两个key的公共子串（可能不止两个），比如"the Car"和
"The Color"共享长度是5，即"The C"，后面非共享的部分分别为"ar"和"olor"
1. **manifest文件**的作用主要是指示层0文件的key range，因为层0会有交叠的情况，
因此查询一个key时可能需要在多个层0文件中寻找（这里层0文件也要按新鲜度排序依次查询）

## Cache
1. 查询会先在memTable中找，如果没找到，会去读index，确定在哪个block中，再去block中读，
这至少需要2次磁盘读取
1. 这里的cache分两种：
  1. TableCache的key为ssTable名称，值包括磁盘文件指针，以及表结构，表结构又包括
  index内容及block信息。当查到某个table时，要判断这个key在不在table中，然后再去查
  block
  1. BlockCache为可选项，它的key是block_id，value是block内容，这样就避免了一次读取。
  这种适合热点读取，如果随机读取并不适合打开BlockCache

## Version
1. 当一次compaction结束后，会创建新版本，当前版本会指向新版本，可用的版本放在
VersionSet中，VersionEdit存在manifest中，表示版本更替的信息，用于重建数据
