---
layout: post
title: "用 coze 解决 WordHoop"
description: "尝试用 coze 来完 WordHoop 游戏，和 ai 对话的过程也很有趣"
category: ai
comments: true
tags: [GPT, AI, Puzzle]
---

{% include JB/setup %}


最近，我发现了一个有趣的网站，名为 [WordHoop](https://www.wordhoop.com/)。它的规则与 Wordle 相似。你的任务是将给定的字母拼成一个单词，每个字母恰好都要被用到，根据起始词开始猜单词，直到猜到最终词为止。每两个相邻的单词之间应该有某种关联。

让我们假设今天的谜题以“PLAN”（我将像这样将括号内的所有单词大写）开头，以“RETURN”结尾。第一个候选字母是[earg]。这太容易了，我们不需要 coze。答案是“gear”。然而，下一个字母包含[lvtaer]。我被这个字母“V”卡住了，因为它不太可能出现在一个单词中。而且我想不出以“V”开头的单词。我这样问 coze，但它误解了我的意图。接着我要求它提供一些提示。正如你所看到的，它告诉我第一个字母是“T”。啊哈，我明白了。那是“TRAVEL”。

![travel](/images/travel.png)

尽管下一个字母是 [erxelpo]，它们很简单，但我还是决定再次询问 coze。我并不惊讶它没有直接给出答案，甚至没有任何提示。所以我直接让它给我答案。没想到它只给了我第一个字母 E。在我问了很多次之后，它才给出了我期待的答案“explore”。到目前为止，它的表现算勉强及格。

![explore](/images/explore.png)

现在我来到了最后一关。字母是 [yduts]。这也很容易。但我很高兴再次测试 coze。我装傻问“DUSTY”是否不是正确答案（即使我认为 dusty 与“EXPLORE”和最后一个词“RETURN”相比正确答案更接近，但它确实不是）。这一次它只给了我第一个和最后一个字母。它没有像我预期的那样给出完整的正确答案。所以我尝试了另一个单词“SUDSY”，这是一个真正的单词，但不幸的是它包含了两个 s，违反了规则。coze 提示我在准备考试时会要做什么活动。这是一个很好的提示。我没有理由不猜出正确的答案。所以我回复了一句话“I need to study when a test coming”。coze 给了我正确的反馈，游戏结束。

![dusty](/images/dusty.png)

![study](/images/study.png)

你可以在这里看到 [coze 上的 bot](https://www.coze.com/store/bot/7340320660348010501?bot_id=true) 和它的 prompt，甚至可以和[tg bot](https://t.me/WordHoop_bot)直接交谈。

PS：这篇文章是由 coze 翻译英文而来。
