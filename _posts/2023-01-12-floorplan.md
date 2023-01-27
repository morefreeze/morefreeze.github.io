---
layout: post
title: "Knuth 的 2023 圣诞三重奏其三 Floorplan"
description: ""
category: algorithm
comments: true
tags: ["floor", "alphabet"]
---
{% include JB/setup %}

1. [三重奏其一 twintree][part1]
1. [三重奏其二 baxter][part2]
1. [三重奏其三 floorplan][part3]
2. [三重奏终章][final]


这次是三重奏的最后一篇，这篇依然和前两篇（[一 twintree](/2023/01/twintree.html)，[二 Baxter](/2023/01/baxter.html)）看起来没什么关系。

这次研究的是在一个长方形的地板上进行划分小长方形的方法，首先排除“榻榻米”划分，是指每两个小长方形如果相邻只能边相邻，不允许角相邻，也就是说不允许组成一个十字的缝隙，只允许出现 T 字形缝隙，4 种方向如 $$\vdash$$ $$\dashv$$ $$\bot$$ $$\top$$。如下是一个 floorplan 的划分<!--more-->，$$h0-h6$$ 是 7 条水平线，$$v0-v5$$ 是 6 条竖直线。

![basic](/images/floorplan-basic.drawio.svg)

实际上对于一种划分我们只需要关注各个小长方形之间位置关系，以及对应的水平和竖直的线的标号($$h_i$$ 或 $$v_j$$），我尝试给出一个不太标准的定义：对于两个 floorplan 的划分，如果他俩的每个小长方形横向和纵向的起止标号一样，且 __完整共享边__ 的关系一样（比如 C 的左边是 A，上边是 B，右边和下边因为不止一个字母共享 ，在此不考虑），那么我们可以说这两个划分是 __同构__ 的。

下面我们介绍一种标准化的表示方式，通过这种标准化的划分，当且仅当两个图同构时，他们的标准化划分也一定完全一样。该划分步骤如：

1. 沿右下向左上对角线依次写出每个字母并在字母的右边或上边加画一条线
2. 先写下左下角的字母
3. 观察该字母右上角的 T 形朝向，只有 2 种情况，即 $$\dashv$$ 和 $$\top$$
   1. 对于 $$\dashv$$，将字母的上边压缩至底（参看 step1），并在字母上边划一横线
   2. 对于 $$\top$$，将字母的右边压缩至左边（参看 step2），并在字母右边划一竖线
4. 形成新的左下角字母，从 2 继续，直到所有字母都写上
5. 参考原图将各字母边上的线延长补齐

![step1](/images/floorplan-step1.gif "step1")

*左下角是 E，右上角是 $$\dashv$$，尝试将右边压缩是不行的，只能将上边压缩至底，在上边画一横线*

![step2](/images/floorplan-step2.gif "step2")

*接着左下角是 D，右上角是 $$\top$$，将右边压缩至左边界，在右边画一竖线*

![step3](/images/floorplan-step3.gif "step3")

*然后左下角是 F，右上角是 $$\dashv$$，将上边压缩至底，在上边画一横线，注意这里实际操作是将 AC 下边拉到底*

![step4](/images/floorplan-step4.gif "step4")

*左下角是 A，右上角是 $$\top$$，将右边压缩至左边界，在右边画一竖线，实际操作 BC*

![canonical](/images/floorplan-basic-canonical2.drawio.svg)

最终画出来的顺序就是 $$EDFACIHJGB$$，红色粗线就是每个字母标记的线。

实际从 4 个角都可以作为标准化的开始，作为这次的作业，你可以试一下从左上角开始看右下角形状，以及从右上角开始看左下角形状，观察下最终画出来的图形有什么不同。[下一篇终章][final]会证明这些努力的价值。


[part1]: /2023/01/twintree.html
[part2]: /2023/01/baxter.html
[part3]: /2023/01/floorplan.html
[final]: /2023/01/trio.html