---
layout: post
title: "learn vim script the hard way 笔记（上）"
description: ""
category: note
comments: true
tags: [vim]
---
{% include JB/setup %}

### CH02

布尔型变量可以用:set [no]number这样来设置，:set number!表示取反，:set number?获取当前状态（实际:set nonumber?也可以哟）
数值型用:set numberwidth=10来设置，同理:set numberwidth?获取当前值
relativenumber或者rnu用来显示相对行号，当前所在行显示绝对行号，两边分别从1,2,3开始显示

### CH03

注意注释不要写在map后面，这样会当成命令去执行map a dd "comment

### CH04

map,nmap,vmap,imap都知道什么意思吧

### CH05

第四章的map都是会循环定义，如:nmap dd O<esc>jddk 这就是一死循环
用noremap,nnoremap,inoremap,vnoremap来表示非递归的map
unmap取消map定义

### CH06

有一些键在normal模式几乎不会用到，可以用来map，如<space>,<cr>,<bs>,-,H,L
vim把prefix的key叫作leader，用:let mapleader="-"来定义，一般会用","作为leader
vim还有种local leader，只作用于当前类型的文件，如py,html，用:lset maplocalleader="\\"来定义

### CH07

本章教你如何更快地去更快地编辑文件（没打错），用:nnoremap <leader>ev :vsplit $MYVIMRC<cr>去打开vim的配置文件，_ev_意味着edit my vimrc file
用:nnoremap <leader>sv :source $MYVIMRC<cr> _sv_意味着source my vimrc file
最好用$MYVIMRC，这样能在不同系统下兼容

### CH08

vim还有个特性叫“缩写”(abbreviations)，与map不同的是他只出现在插入，替换和命令模式
缩写可以用于打错字的时候，如:iabbrev waht what
缩写会替换“非关键字符”，这货是啥，用:set iskeyword?看一下
经常会看到这样iskeyword=@,48-57,_,192-255，这表示关键字符是所有英文大小写字母，数字（48-57），下划线，另外一些特殊字符（192-255）
你可以看:help isfname了解完整描述，但它货挺长的……（这个实际是vim定义哪些字符可以成为文件名，注意里面没有空格和反斜杠\）
缩写另一个用处是可以快速输入用户或版权信息，如:iabbrev @@ morefreeze@gmail.com
缩写和map的区别是map一旦发现能匹配上就转换，而缩写需要确认这是个整词（就是isfname定义的）才会替换，假如:inoremap ssig hehehe，如果输入Lessig，会发现后面被替换了，而换成缩写就没有问题

### CH10

有几种办法可以退到normal模式，
esc
<c-c>
<c-[>
尝试:map jk <esc>或者:map jj <esc>
你要蛋疼想训练你的肌肉记忆新的map，你可以:inoremap <esc> <nop>（训练上面的jk反应）注意：这里我尝试把<esc>disable掉了，但出现了delete键失灵的情况，在插入模式按下会插入'[3~'，即使用vim wiki上的:fixdel也不管用，所以这里建议尽快训练好jk反应

### CH11

:nnoremap <buffer> <leader>x dd这句只会作用在当前光标在的那个窗口，切换到另一个窗口这句就不好使
一般是不像上面那样写<buffer>的，而是写<localleader>，这类似命名空间，假如你写插件的话，这样会防止你写了半天的map被别人覆盖掉
还有:setlocal wrap来只对当前窗口有效
如果local和普通的map都是同一个值的话，会优先执行local的map
localleader一般用于文件类型的插件
想知道一个键是否被map可以用:verbose imap <c-h>

### CH12 Autocommands

正常如果打开一个新文件，并且马上退出，这个文件不会留在硬盘上，如果你执行:autocmd BufNewFile * :write则会让文件留在硬盘上
我们来解析下这条命令，BufNewFile是vim要监控的事件，*是要过滤的事件，:write要运行的命令
命令那部分是不允许出来<cr>这种的
事件的类型有（只是一小部分）：
开始编辑一个不存在的文件
读一个文件无论是否存在
切换文件的filetype设置
一段时间内没有按键盘上的某个键
进入插入模式
退出插入模式
:autocmd BufNewFile *.txt :write这是对.txt后缀的文件进行过滤，只保存这类文件
可以同时有多个事件:autocmd BufWritePre,BufRead *.html :normal gg=G，在预写和读的时候格式化.html文件
提一下BufNewFile和BufRead几乎总是同时出现
文件类型相关的例子:autocmd FileType python nnoremap <buffer> <localleader>c I#<esc>，当打开一个Python文件时，使用<leader>c 可以快速注释
通过:help autocmd-events查看更多的事件列表
在做习题时，发现可以map <buffer> <leader> yyyy而不能map <buffer> <localleader> yyyy，注意这里需要先设置localleader，我猜你就没设:let localleader="\\"
