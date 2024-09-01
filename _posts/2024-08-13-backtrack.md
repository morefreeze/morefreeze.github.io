---
layout: post
title: "从零单排回溯算法 algorithm B"
description: ""
category: article
comments: true
tags: [backtrack, knuth]
---

{% include JB/setup %}


## 引言

当我要介绍 Knuth 在23年圣诞节时的演讲 Dancing cell时，我发现我缺少了太多的上下文，算法虽然不难讲清楚，但为什么要这么做，这个算法有什么应用价值我并不清楚，视频中提到了这是从 TAOCP 的7.2.2开始的，翻看了整个第7章，发现整章都在讲回溯算法，包括上一篇说的 dancing link 实际是比较优化的算法了，回溯算法解决的就是各种枚举问题，当没有特别优化的算法时这可能是唯一能产生解的算法了，于是我决定从头好好学一学。
<!--more-->

## 回溯基本法
还记得当我用 Pascal 写一些回溯算法（具体来说是DFS）时，我都会先写一个dfs(0)，可能还有一些保存当前解法的参数，但至今都不能总结出一个模板，讲搜索的过程抽象。而 Knuth 这里直接给出了基本回溯的一般操作框架，我们只要找到素有的序列 $ x_1x_2...x_n $ 使得属性 $P_n(x_1,x_2,...,x_n)$ 满足条件，每个$x_k$的取值来自于定义域 $D_k$。这里他给出了基本回溯法的 2 个条件，也可以说是剪枝：

$$每当P_{l+1}(x_1,...,x_{l+1})为真时，P_l(x_1,...,x_l)为真  \tag{1}$$
$$如果P_{l-1}(x_1,...,x_{l-1})成立时，P_l(x_1,...,x_l)相当容易测试  \tag{2}$$

接下来描述了一个通用的回溯法框架，总共分 5 步，中间 3 步是核心部分：

1. 初始化，令$l\leftarrow1，初始化一些必要的数据结构，这里$P_0()始终成立$
2. 进入第$l$层，现在$P_{l-1}(x_1,...,x_{l-1})$成立，如果$l>n$跳到第 5 步，否则令$x_l\leftarrow min D_l$，即从$D_l$中取出最小的值尝试
3. 尝试$x_l$，如果$P_l(x_1,...,x_l)$成立，更新数据结构，令$\leftarrow l+1$，然后重复第2步
4. 接着尝试，如果 $x_l\neq max D_l$，令$x_l$是下一个$D_l$的元素，然后重复第2步
5. 回溯，这时已经测试到$l>n$，如果$l>0$，那么还原在第 3 步做的操作，然后回到第 4 步

总觉的这么顺序描述很不舒服，所以还是用伪代码表示下：

{% highlight python linenos %}
l = 0
cur_step = []   # step 1
def dfs(l, cur_step):
    if l > n: # step 2 go to step 5
        print_solution(cur_step)
        return # step 5
    for x in d[l]: # step 2
        if p[i](cur_step):  # step 3, go to step 2
            cur_step.append(x)
            dfs(l+1, cur_step)
            cur_step.pop(-1)    # step 4
    return # step 5
{% endhighlight %}

这里唯一要注意的是：第 4 步只说了如果 $x_l\neq max D_l$的情况，当$x_l= max D_l$时，也是往后走到第 5 步进行回溯。

### 4 皇后
下面回到经典的 n 皇后问题，这里 n = 4为例。令$x_k$是第 $k$ 行皇后的位置，那么任意$x_j\neq x_k$，还有对角线不能攻击到，有$|x_k-x_j|\neq k-j$，这些条件其实就是$P_l(x_1,...,x_l)$要验证的事。让我们手工一步步模拟下回溯算法。

假如$x_1\leftarrow1$，当$l=2$时，$P_2(1,1)$和$P_2(1,2)$都为假，当$x_2\leftarrow3$时我们才能接着往下走，$l\leftarrow l+1$，然后我们就发现$P_3(1,3,x)$都不成立。退回到$l=2$，接下来尝试$x_2\leftarrow4$，然后$x_3\leftarrow2$，但$l=4$无论如何都放不下了，一路回溯到$l=1$，接着尝试$x_1\leftarrow2$，最终发现$x_1x_2x_3x_4=2413$是一个解。

## 小结
至此基本回溯算法就说完了，框架并不复杂，可以看到即使上面的伪代码，也几乎可以直接拿来解 n 皇后问题，我们后面会不断增加条件，让题目看起来更复杂，也会发现新的数据结构加速剪枝，但万变不离其宗
