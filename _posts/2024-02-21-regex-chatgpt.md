---
layout: post
title: "《挑战24个正则表达式难题》读后感"
description: "虽然《挑战24个正则表达式难题》这本书关于ChatGPT的部分只是噱头，但一些有趣的正则谜题还是值得拿出来玩味地"
category: technology
comments: true
tags: [正则, GPT, AI, Puzzle]
---

{% include JB/setup %}

* Table of Contents
{:toc}

最近在找 ChatGPT 相关的书，偶然看到了这本《Copilot 和 ChatGPT 编程体验：挑战 24 个正则表达式难题》正好学学正则顺便看看别人怎么用 GPT。
看完之后我的评价是正则学了一些，当然这些语法你可以在网上随便搜一下学到，但最后还是有几个有意思的例子值得揣摩。然后是关于 GPT 这部分完全是个噱头，<!--more-->简短来说 LLM 几乎都解决不了难一些的正则问题，除非这些问题是比较经典的，比如匹配 IPv4 地址。最后说下翻译，没猜错的话应该是拿 GPT 硬翻的，很多地方语句都不通顺，有些编程名词翻译一看就不对，比如代码的 comment 翻译成评论，甚至有的连题目都翻译不清楚，需要靠自己看样例学习。总之，我主要学习正则写法，烂的翻译影响阅读体验但不妨碍学到东西。下面我会列举几个有意思而且我学到了一些东西的例子。

💡 阅读之前我要假设你已经了解大部分的正则语法，包括前行（零宽）断言等高级语法，并且自己从零写过一些正则。

## 难题 6 灾难性回溯

⚠️ 我会改编下这道题，原题有些不必要的字符变换。

> 有两个字符集合 1[ABC]和集合 2[CDE]，给定一个字符串，每个词可能由**0 个或 1 个空格**分隔，如果一个词由集合 1 构成，我们称为词 1，同理，还有词 2。一个词 1 后**必须**跟着一个词 2，然后可以有下一组词 1 跟词 2，判断这个字符串是否由词 1 后跟词 2 的组合构成。

例如：
`A(1)E(2) AB(1)C(2)BC(1) D(2)`

注意两个集合有相同的字符 C，那么如果我们直接写出一个直白的正则匹配，像下面这样

`^(([ABC]+) ?([CDE]+) ?)+$`

在字符串包含很多的 C 后接不在集合 1 或 2 的字符时（如 20 个 C 后跟一个 Z），正则引擎（具体来说是 NFA）会因为要尝试判断它是属于集合 1 还是集合 2 而让匹配过程变成指数时间，解决办法是什么呢，首先判断所有字符是否在 2 个集合里，当有不在的字符时提前返回，刚才的正则改进一下：

`(^(?=[^ABCDE ]+$)(([ABC]+) ?([CDE]+) ?)+)$`

可以看到`(?=[^ABCDE ]+$)` 前行断言先判断字符是否都在集合里，不在就不会进行后面的匹配了。

📝 不过说真的，你遇到过自己写的正则匹配非常慢的情况吗？留言告诉我。

## 难题 9 传感器艺术

当你在用正则的时候，就要用正则的思维来思考。

> 定义一些符号表示一系列的波形变换，
> 波形的变换要从低到高或从高到低，突变不受此限制直接转换到另一边，
> 写一个正则验证是否符合规则。波形符号如下

| 含义                     | 表示 |
| ------------------------ | ---- |
| 低波                     | L    |
| 高波                     | H    |
| 从低到高                 | u    |
| 从高到低                 | d    |
| 突变（即从一边到另一边） | F    |

例如一个合法的例子：

```plain
_/^^^\_/^|___|^\____|^^\__/  # 图形化表示
LuHHHdLuHFLLLFHdLLLLFHHdLLu  # 字母表示
```

<details>
  <summary>建议你先自己想一想，再往下看答案。</summary>
 这题的诀窍是每次考虑相邻的两个符号，枚举所有的可能<pre>^(((?=LL|Lu|LF|HH|Hd|HF|uH|dL|FH|FL)|(?=.$))[LHudF])+$</pre>
</details>

---
## 难题 13 德扑

> 正则实现匹配德扑的各种牌型，这里允许用 Python（或别的语言）来分别判断符合哪种牌型

德扑的牌型我相信你一定能随便搜到，就不在这里赘述，并且牌型太多，我只挑有意思的几个来说。

### 判断顺子

这里要依赖按先点数后花色排序，这个正则做不了，假设 hand 是个字符串存了排序后的手牌，例如：`JD TD 9C 8D 7H`，这就简单了，只要把花色删除留下点数，判断是否连续

{% highlight python linenos  %}
def is_straight(hand):
  h = re.sub(r'[ SHDC]', '', hand)  // SHDC表示4种花色
  return re.search(h, 'AKQJT98765432')
{% endhighlight %}

### 判断四条

（这次不要求手牌有序）四条的判断有点奇妙，首先只留下点数，按程序语言的思路然后判断是否有数字出现了 4 次，但正则是不能计数的，所以这里要重新思考怎么判断 4 次，注意到出现 4 次的点数不在第一位就必定在第二位，那么：

{% highlight python linenos  %}
def is_four_of_kind(hand):
  h = re.sub(r'[^2-9TJQKA]', '', hand)  # 只留下点数，其他都删掉
  return re.search(h, r'^.?(.)(.*\1){3}')
{% endhighlight %}

解释下第三行的正则， `^.?` 用于匹配多余的那一个点数，当匹配上就是对应重复的点数在第二位的情况，没匹配上对应在第一位的情况。接着第一个捕获组捕获重复的点数，第二个捕获组 `(.*\1)` 用 `\1` 表示第一捕获组，`.*` 用来捕获的多余点数，例如 63666，第二捕获组在第一次（后面有个{3}意思要匹配三次，这次是第一次）会匹配到 36，也相当于有了一个 6。细心的你可能发现这样写对于 6363666 也可以，但别忘了德扑最多 5 张牌。

## 难题 18 识别相同计数

> 这题是用正则捕获一定个数的匹配，例如 n 个 A 后跟 n 个 B，n 是个变量

例如：AAABBB 符合，AAAAABBBBB 也符合。但很遗憾，因为 NFA(Nondeterministic Finite Automaton) 不提供存储数字的变量和堆栈，使得正则无法实现很多编程语言的功能，其中包括这道题。

## 难题 20 IPv4 地址

> 经典题目，匹配 IPv4 格式的地址

这里关键在于正则没有表示数值的方式，只能通过字符串的枚举来达到从数字 a 到数字 b 的范围匹配，诀窍是按百十个位依次枚举，不多说直接上答案：

```plain
25[0-5]|2[0-4]\d|[01]?\d\d?
```

可以考虑更一般的匹配，例如匹配 0-4096

## 难题 21 匹配倍数序列

> 匹配 ¥ 符号的个数，以空格分隔，后一段必须是前一段的两倍，注意这题要求很严格，必须整个串都是这种倍增的关系。

例如（注意最后还要有个空格 ⎵）：

```plain
¥ ¥¥ ¥¥¥¥ ¥¥¥¥¥¥¥¥⎵ // 1 2 4 8 ok
¥¥¥ ¥¥¥¥¥¥⎵ // 3 6 ok
¥ ¥ ¥¥ ¥¥¥¥⎵ // 1 1 2 4 bad
```

诀窍在于用先行断言维护【后一段是前一段两倍】这个条件，上答案：

```plain
^(((¥+) )(?=\3\3 ))+(\3\3 )$
```

首先明确下 `\3` 指的就是最里面括号 `(¥+)` 这段，后半段`(?=\3\3 ))+(\3\3 )` 即上面提到的条件，如果你尝试删掉先行断言这一段，会发现第 3 个例子也能匹配，这相当于在字符串最后有一组倍增关系满足就行，没有了先行断言，就相当于每组相邻的两段的关系断了。

## 难题 22 斐波那契数列

> 有了上一题的经验，斐波那契数列匹配应该不是问题，只是这次要用到上一段和上上一段，判断是否符合斐波那契数列

这里为了可读性，用了多行模式，空格需要用`\`或者`[ ]`写法来和字面空格区分，答案有点长：

{% highlight python linenos  %}
pat = re.compile(r"""
 ^
 (                    # 捕获将要重复的段
  ((¥+)\ (¥+)\ )      # 前两个段，注意不要求一定从1 1开始
  (?=$|\3\4[ ])       # 断言结束或者\3接着\4后跟一个空格
 )+                   # 两段算一组，至少出现一组
 (¥+\ )?              # 字符串最后一段，已经在断言判断过\3\4，因此可以放心匹配
$
""", re.VERBOSE)
{% endhighlight %}

这个神奇的正则居然能匹配出斐波那契数列的 ¥，但如作者所言，这个正则有个弱点，它只能匹配所有第奇数个开始的 3 个数是否符合加和关系，不能匹配从第偶数个开始的，例如`¥(1) ¥¥(2) ¥¥¥(3) ¥¥¥¥(4) ¥¥¥¥¥¥¥(7)`，可以看到从第 1 个和第 3 个开始的是 1+2=3，3+4=7，而第 2 个开始 2+3<>4，所以这里还要借助 Python 处理一下：

{% highlight python linenos  %}
pat = re.compile(....)
def is_fib(s):
  match1 = re.search(pat, s)
  match2 = re.search(pat, s.split(' ', 1)[1])
  return match1 and match2
{% endhighlight %}

`s.split(' ', 1)[1]` 相当于剃掉第一个空格（含）之前的内容，也就是检查原串的所有偶数开始的序列，到此，这个斐波那契数列判断完满解决。

## 难题 24 匹配互质

> 假设由空格分隔 ¥ 的个数已经按升序排列，匹配两两互质

例如：

```plain
¥¥ ¥¥¥ ¥¥¥¥¥ ¥¥¥¥¥¥¥ ¥¥¥¥¥¥¥¥¥¥¥  // 2 3 5 7 11 ok
¥¥ ¥¥¥¥¥ ¥¥¥¥¥¥¥¥¥                // 2 5 9 ok
¥¥ ¥¥¥ ¥¥¥¥                       // 2 3 4 bad 2,4是合数
```

虽然筛法直接筛质数不行，但这次可以。

诀窍是利用负向前行断言把后面是当前倍数的匹配出来（所以题目要求是升序，小的倍数才能负向匹配到大的），上答案：

```plain
^((¥¥+) (?=\2¥)(?!.* \2{2,} ))+
```

相信通过前面的学习你已经能自己解读这个正则，就当成一个小作业吧。注意这个正则不会捕获最后一个“数字”，它只能判断是否匹配。

## 附录

从最后的几个难题，我重新理解了断言的用法，其实前行断言，指的是右边满足匹配，但不计入匹配，
例如 `(?=[a-z]{3})(.*)` 意思当有三个小写出现时匹配，`.*`仍包括三个小写，后行断言，指的是左边满足匹配。
正向负向，分别指满足匹配和不满足，能和前行后行断言组合，最后就有了 4 种组合形式，如下：

| 正负/前后 | 前行           | 后行           |
| --------- | -------------- | -------------- |
| 正向      | 右边要求满足   | 左边要求满足   |
| 福祥      | 右边要求不满足 | 左边要求不满足 |

## 番外 斐波那契的完美解

在读完斐波那契这一章后，我发现书里匹配思路和上一章倍数序列完全不同，而且还需要再次分割字符串额外校验，所以我尝试用倍数序列的思路来解决这题。

整理下思路，验证涉及到三组，我们称为 g1,g2 和 g1g2，我们需要一次只消耗 g1 这组，剩下的 g2 和 g1g2 就在前行断言里，当这三组满足后，向后移动一组继续匹配（因为只消耗了一组），于是有了下面的表达式，为了可读性，我用了`(?P<g1>)` 命名捕获组叫 g1，用`(?P=g1)`使用 g1 匹配到的内容，代码如下：

{% highlight python linenos  %}
pat2 = re.compile(r'''
    ^(
        (?P<g1>¥+)[ ]               # 匹配第一组
          (?=                       # 开始前行断言
            (?P<g2>¥+)[ ]           # 匹配第二组
            ((?P=g1)(?P=g2)\ )      # 匹配第三组是第一组接着第二组
          )
        )+                          # 继续循环，注意字符串实际只会消耗第一组，下次消耗第二组，最终只能匹配到倒数第三组，因为前行断言还需要2组
        (
            (¥+)[ ]                 # 这里已经不需要精确地用g1g2表示了，因为在倒数第三组时已经前行断言过了
            (¥+)[ ]                 # 匹配最后一组
        )
    $''',
    re.VERBOSE)
{% endhighlight %}

## 参考

- <https://regex101.com/>
- <https://regexper.com/>
- <https://deerchao.cn/tutorials/regex/regex.htm>
- <https://zq99299.github.io/note-book/regular/04/>
