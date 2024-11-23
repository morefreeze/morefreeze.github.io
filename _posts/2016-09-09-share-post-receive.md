---
layout: post
title: "Share post receive hook"
description: ""
category: tech
comments: true
tags: [git]
---
{% include JB/setup %}

I had shared a precommit [here](/2016/05/share-precommit-hook.html) which help you check your code before your commit.
If you want to deploy it on test machine even production machine, you may need this.
<!--more-->

You just change `DEPLOY_ROOT` and `DEPLOY_ALLOWED_BRANCH` variable.
I suggest change `DEPLOY_ALLOWED_BRANCH` to `dev` instead of master if you deploy to test machine.
Here is the [code](https://gist.github.com/thomasfr/9691385#file-post-receive).

Put `post-receive` in `hooks/` of your remote repo. Set executable to it with
`chmod u+x hooks/post-receive`. Just type `git push remote dev` and enjoy it!
