---
layout: post
title: "learn vim script the hard way 笔记（上）"
description: ""
category: note
comments: true
tags: []
---
{% include JB/setup %}

[上一篇](/2017/06/learn-vim-script-the-hard-way.html)
### CH13 Buffer-Local Abbreviations
1. 这章就是说`iabbrev`也能用`<buffer>`来修饰
2. 你想记住某个新的snippet最好办法就是disable掉原来的命令，比如`iabbrev <buffer> return NOPENOPENOPE`

### CH14 Autocommand Groups
1. `autocmd`是不会替换原先的命令的，假如使用两次同样的命令，那触发autocmd时会进行两次命令
2. 特别要注意在你`source $MYVIMRC`时，autocmd会再载入一次！
3. 可以用`augroup testgroup autocmd xxx augroup END`，这时如果你运行下`augroup testgroup autocmd yyy augroup END`，你猜`xxx`还会执行吗？耶，答案是会！
4. 你可以在augroup里用`autocmd!`来清空augroup
<!--more-->

### CH15 Operator-Pending Mappings
1. vim有一类命令后面可以接动作，比如`d`,`y`,`c`
2. `onoremap p i(`，如果在普通模式下输入`dp`，相当于`di(`，就是把括号内的内容删掉
3. `:onoremap b /return<cr>`，输入`db`，会向下删除，直到遇到**return**为止
4. `:onoremap in( :<c-u>normal! f(vi(<cr>`，输入`cin(`会直接将光标移到一个括号，并且删除括号内的内容，然后变成插入模式，`<c-u>`之后会讲，这里没什么用，只是保证能在所有情况下运行，`normal! dddd`表示在普通模式下按`dddd`（删除2行），`f(`表示前进到最近的左括号，`vi(`表示选中括号内的内容，别忘最前面是`c`，所以相当于改变括号内的内容
5. 定义延迟map有两个规则：
    1. 如果你定义的内容是一段选中的内容，则vim会直接操作这段内容
    1. 否则vim会操作原光标到到新位置的内容
1. `<c-u>`可以通过`:help omap-info`查看，但**没懂**，用于移除vim可能插入的范围（"The CTRL-U (<C-U>) is used to remove the range that Vim may insert."）

### CH16 More Operator-Pending Mappings
这章讲了更复杂的延迟map的例子，比如`:onoremap ih :<c-u>execute "normal! ?^==\\+$\r:nohlsearch\rkvg_"<cr>`，在Markdown里，当光标在内容中时，会选中heading，下面逐字翻译下
1. `:normal gg`相当于普通模式下执行`gg`，跳到文件头
3. `:execute "normal! gg"`和上面是一个效果
4. `:normal! gg/a<cr>`就不是你想的那样，因为normal无法识别特别字符，比如`<cr>`，但是，你可以用`:execute "normal! gg/a\r"`来完成，注意，将`<cr>`替换成了`\r`
5. 另一个值得注意的地方是，给出的命令最后用了`g_`而不是`$`，他俩都是到当前行最后一个字符，但`$`会多匹配一个，你感受一下
6. `normal!`中的感叹号是表示不使用map
7. `:help normal`,`:help execute`,`:help expr_quote`也许会有用

### CH17 Status Lines
1. `:set statusline=%f`设置状态栏为显示文件名
2. 注意后面如果有`空格`的话，要用`\ `（斜杠后有个空格）来转义，否则会认为是set命令的下一条，因为set支持一次设置多个
3. 一次写一整行的状态栏太复杂难懂了，可以分开写，只要`:set statusline=%f`,`:set statusline+=\ -\`,...
4. `:set statusline=[%4l]`的%4表示占4个字符，不足用空格补齐，`%-4`表示左对齐，`%04`表示不足用0补齐，`%.20`表示占20个字符的宽，多的会截掉，一般格式为`%-0{minwid}.{maxwid}{item}`

### CH18 Responsible Coding
1. 多写注释
2. 可以用`" Vimscript file settings ---------------------- {{{`和`: }}}`来包住一个想被折叠的部分，同时需要设置`:setlocal foldmethod=marker`，在这部分内容中时，按`za`来折叠或打开
3. vim有许多缩写的命令，比如`setl`==`setlocal`，但十分不建议在vim script里这么写，如果你是临时手写命令的话，可以用缩写

### CH19 Variables
1. 用`:set foo='bar'`对变量赋值
2. `:set textwidth=80`，用`:echo &textwidth`获取选项的变量值，对bool值也可以会用，如`:let &wrap=1`
3. 对选项变量的值进行赋值也相当于修改选项，如`:let &textwidth=100`,`:let &textwidth=&textwidth+10`
4. 你可以用`:let l:number=1`设置local变量
5. 用`:let @a='hello'`设置一个寄存器变量，`@"`是复制时的内容，`@/`是按`/keyword`中的keyword内容
6. bool值不可以用纯字母的字符串，如果是'42','0'这种还是可以转换成数字1或0的
7. 可用的寄存器有"-a-zA-Z0-9"（寄存器0存最近一次y的内容，1存最近一次删除或改变的内容，如果少于一行的话或指定别的寄存器，则不存，当还有删除或改变时，会将1的内容移到2，依此类推）
1. 未命名寄存器`"`（vim的`d`,`c`,`s`,`x`,`y`的内容，也包括上一个用名字的寄存器的内容）
1. 4个只读寄存器`:.%#`（`:`保存上一条命令，`.`保存一次输入内容，`%`当前文件全路径，`#`备用文件全路径），表达式寄存器`=`（这不是一个真的寄存器，只是在一些命令中表示这里是一个寄存器）
1. 选择或drop寄存器`*+~`（这在GUI界面才有）
1. 黑洞寄存器`_`（当使用`"_dd`时，将不存储dd的内容到任何寄存器）
1. 还有搜索寄存器
1. 其他更多寄存器看`:help registers`吧
8. `:display`显示所有寄存器的值
9. 经常会有想把复制的内容（用`y`复制，并非剪切板）用在搜索上，或其它地方，这时可以用`<c-r>`后面再跟寄存器名，比如`<c-r>0`就是刚才复制的内容，这时会自动替换成刚才复制的值

### CH20 Variable Scoping
1. `:let b:foo='bar'`，设置变量作用域是当前buffer
2. `:help internal-variables`查看都有哪些变量作用域
3. 前面什么都不写，变量是当前作用域，在函数里就只到函数结束，否则就是全局，其他修饰符有`b:`（当前buffer）,`w:`（当前窗口）,`t:`（当前tab）,`g:`（全局）,`l:`（当前函数内的变量）,`s:`（当前使用`:source`的vim脚本）,`a:`（函数参数，只在函数内有效，和`l:`的区别是`l:`可以随便定义变量，而`a:`只限于函数传进来的参数）,`v:`（全局，vim预定义变量）
4. 可以用`:for k in keys(b:) | echo k | endfor`看到buffer作用域下的变量

### CH21 Conditionals
1. 多行命令可以用`|`连接起来，而且要注意，除了开头要有**冒号**外，`|`后面的命令不需要有**冒号**
2. 当判断是个字符串时，会先尝试转成数字，然后再转成bool，比如"10foo"相当于10，同时也可以进行运行`"10foo"+10`，将会得出20，类似PHP的处理方法
3. `:if 1 | echo 'true' | elseif 2 | echo '2' | else | echo '3' | endif`

### CH22 Comparisons
1. 如果`:set ignorecase`，则`:if 'foo'=='FOO'`就是真了
2. 这个故事告诉我们写脚本时要假设用户的各种设置，不要相信裸的`==`，而要用`==?`表示大小写不敏感的相等，用`==#`大小敏感的相等，其实大部分比较都支持`?#`，比如`!=#`,`>=?`
3. 还有种`smartcase`会在模式串都是小写的情况下，认为是大小写不敏感，其他情况认为是敏感的
4. `\c`出现在模式串的任何位置都表示这个串是大小写不敏感，`\C`表示敏感，如`\cfoo`

### CH23 Functions
1. vim的函数都要**首字母大写**
2. 使用`:function Meow() | xxxx | endfunction`定义一个函数
3. 使用`:call Meow()`调用一个函数
4. 一个函数最多有**20**个参数

### CH24 Function Arguments
1. vim的函数可以接受参数哟，在函数内使用`a:xxx`来使用
2. 函数可以接受变长参数列表，用`:function Varg(...)`，参数值是`a:0`这是参数个数,`a:1`这才是第一个参数,`a:000`是**可变**参数列表（注意如果是`:function Varg2(foo, ...)`的形式，`a:000`只会显示...的参数内容），`a:1 == a:000[0]`
3. 参数`a:xxx`是**只读**变量，试图赋值会报错

### CH25 Numbers
1. vim的数字有2种，一种是有符号32位整数，一种是单浮点数
2. `echo 0x10 017`
3. `echo 5.45e+3`
4. `echo 3/2`整除，`echo 3/2.0`浮点数

### CH26 Strings
1. `:echom 'Hello' + ' world`会显示0，因为vim的+只对数字有用，这里字符串都转成了数字
2. `:echo 10 + '10.10'`会显示20，因为`10.10`是个字符串会转成10
3. 字符串连接用`.`
4. `:echo 10.10 . 'hehe'`会报错，因为vim很愿意把字符串转成浮点，但反之不行
5. 转义符是`\`
6. 如果用`:echom abc\nefg`，`\n`会显示成`^@`，这是表示新换行的另一种形式
7. 用单引号表示不进行转义，`:echom 'That''s enough'`会显示成`That's enough`，两个单引号''是这里唯一的转义
8. 通过`:help expr-quote`可以知道，`\x`,`\001`这种就不说了，`\u02a4`或`\U02a4`表示**当前编码**（`encoding`）下的字符值，`\b`表示删除，`\e`表示`<esc>`，`\f`表示`formfeed`(`<FF>`)
9. 用`<c-v>`或`<c-q>`来插入非数字的字面值，比如Tab，比如`<c-v>065`就是插入'A'
10. 一般模式匹配的时候用单引号比较好，省去转义\的麻烦，例如`a =~ '\s*'`

### CH27 String Functions
1. `strlen`,`len`测字符串的长度
2. `split(expr[, patt[, keepempty]])`会把字符串按patt切分成List类型，如果patt是`xxxx\zs`则会保留被切掉的部分，keepempty表示前几部分可以是空，如果不写默认是0，则返回的第一个元素一定是有值的，`join(List, glue)`会用glue把List粘成一个字符串
3. `tolower`,`toupper`转换大小写

### CH28 Execute
1. `execute`就是为了给字符串估值，然后去执行，比如`:execute "vsplit " . bufname('#')"`
2. vim的`execute`不像其他语言的`eval`那样危险，因为vim很少接受用户输入，即使接受也是当前用户，反正那是他们的电脑，第二个原因是vim有一些难懂的语法，但`execute`是最简单的，而且能把多行弄成一行写，见下例子
3. `execute`通常用来追加那些不能用|追加的命令，比如`:execute '!ls' | echo 'abc'`
4. 也可用于要打`:normal`的情况，如`:execute  "normal ixxx\<esc>"`，效果是切换到插入模式，输出`xxx`然后按`<esc>`

### CH29 Normal
1. 用`:normal G`就相当于在普通模式下执行`G`跳到文件最后
2. `:normal`也会忠实地使用任何能用的map，如果`:nnoremap G dd`，则`:normal G`会相当于删除一行
3. 可以用`:normal!`来执行原来的命令的意思
4. 但是在`:normal!`无法识别特殊字符，如`<cr>`，会当成小于号字符串cr和大于号
5. `:helpgrep`是跳到与后面模式匹配第一个的帮助上，可以用`:cwindow`或`:cnext`来切换，`:helpgrep uganda\c`忽略大小写

### CH30 Execute Normal!
1. 使用`:execute normal! gg/foo\<cr>`就可以接受特殊字符了！

[下一篇](/2017/06/learn-vim-script-the-hard-way-c.html)
