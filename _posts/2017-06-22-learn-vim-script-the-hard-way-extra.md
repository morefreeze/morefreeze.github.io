---
layout: post
title: "learn vim script the hard way 笔记（番外）"
description: ""
category: note
comments: true
tags: []
---
{% include JB/setup %}

### CH41 Creating a Full Plugin
1. 看到这里你可以停了，因为前面的姿势足够你完善自己的`~/.vimrc`脚本，去修复别人脚本的bug了，绝无讽刺的意思
2. 往下学之前，建议先玩下[Potion](http://perl11.org/potion/index.html)语言，这是个很小的语言，使用它的目的是为了辅助我们写vim script

### CH42 Plugin Layout in the Dark Ages
1. `~/.vim/colors/`在这里的文件记录了vim的颜色主题，如果运行`:color xxx`就能看`~/.vim/colors/xxx.vim`的配色方案了，查看当前配色都有哪些用`:hi`
2. `~/.vim/plugin/`在这里的文件每次vim启动都会运行一次
3. `~/.vim/ftdetect/`这里的文件每次启动也会运行一次，`ft`的意思是`filetype`，这里的文件应该是包含`autocmd`用来切换filetype的，所以一般就**一行**
<!--more-->

4. `~/.vim/ftplugin/`这里的名字**非常重要**，如果你`:set filetype=derp`，则会找`~/.vim/ftplugin/derp.vim`，有就运行它，同时也支持目录，也会在`~/.vim/ftplugin/derp/`下找，这样有利于分组
5. `~/.vim/indent/`这里的文件是用于不同ft的缩进排版的，文件名规律同`ftplugin`，这里只能设置**local-buffer**，这个实际和`ftplugin`没啥区别，但分开放有利于理解
6. `~/.vim/compiler/`这个和`indent`又非常相像，只是它做的是编译器相关的
7. `~/.vim/after/`这个是在`~/.vim/plugin/`启动后启动，这个作用就是有的插件为了防止和其他插件的快捷键冲突又重定义一下
8. `~/.vim/autoload/`这个比较复杂了，后面会讲
9. `~/.vim/doc/`放插件文档的地方

### CH43 A New Hope: Plugin Layout with Pathogen
1. 上面是以前的vim文件布局，新装插件需要手动解压然后BLABLA，如果作者删个文件你咋办？如果有个脚本（比如在autoload下）重名你是不是SB了？现在我们有了[Pathogen](http://www.vim.org/scripts/script.php?script_id=2332)简直就是屌
2. vim有个变量`runtimepath`，在搜索文件的时候也会去这里找，比如`syntax/`下的文件
3. Pathogen会自动将`~/.vim/bundle/`下的目录加进`runtimepath`里，在这里的每个目录下都会包含一些vim的目录，比如`colors/`，如果你在这下面用了版本控制，比如Git,那你直接`git pull orgin master`就行了啊
4. 译注，整篇文章成文较早，当时vim 的插件管理并不像现在这么多，有兴趣的可以看看[这里](https://vi.stackexchange.com/questions/388/what-is-the-difference-between-the-vim-plugin-managers)

### CH44 Detecting Filetypes
1. 我们要针对一种编程语言`potion`进行一些插件设置，首先新建一个`~/.vim/ftdetect/potion.vim`，输入`au BufNewFile,BufRead *.pn set filetype=potion`，这就告诉vim对于任何 pn 结尾的文件，设置`filetype=potion`
2. 可以`:set filetype=c.doxygen`，点号用来分隔两种文件类型，会先用c，再用doxygen
3. 一般会用`:setfiletype`而不是`:set filetype`，因为前者设完后会只载入一次插件或语法文件

### CH45 Basic Syntax Highlighting
1. 新建一个语法文件`~/.vim/syntax/potion.vim`
    ```vim
    if exists("b:current_syntax")
        finish
    endif
    echom "Our syntax highlighting code will go here."
    let b:current_syntax = "potion"
    ```
    注意用`b:current_syntax`保证互斥，不会被载入两次
2. 加入
    ```vim
    syntax keyword potionKeyword to times
    highlight link potionKeyword Keyword
    ```
    定义`to`,`times`是关键词，然后连接potion关键词到关键词组（这个XX组就是决定了一套配色，比如函数是蓝色）
3. 上面`syntax keyword {group-name} [{options}] {keyword} ... [{options}]`，注意syntax后的keyword是固定的，接着是自定义的组名，再接着是关键词，关键词要满足`iskeyword`

### CH46 Advanced Syntax Highlighting
1. 由于一般注释都是用`#`，而`#`又不是`iskeyword`，所以我们要用正则去匹配及它后面的内容
    ```vim
    syntax match potionComment "\v#.*$"
    highlight link potionComment Comment
    ```
    `\v`表示"very magic"，对于`|()`这种就不需要加`\`转义了，这里还要注意`syntax match`是不支持放在组里的
1. `hi link`的位置可以任意放，放匹配前面也可以
2. 优先级是先按最后匹配的来，然后`Keyword`大于`Match`和`Region`，最后(匹配开始较前的)优先于(匹配开始较后的)
3. 匹配的两端必须保证是一样的字符，比如可以是+"+（这和正则的匹配规则是一致的）

### CH47 Even More Advanced Syntax Highlighting
1. 想学习更高端的语法文件配置是继续读`:h syntax`或者看别人写的
2. 这次我们用`syntax region`来匹配字符串
    ```vim
    syntax region potionString start=/\v"/ skip=/\v\\./ end=/\v"/
    highlight link potionString String
    ```
    `skip`是用来跳过字符串中所有以反斜杠和一个任意字符的（当然也包括引号），其实这里用`skip=/\v\\"/`也可以，但应该是为了兼顾单引号的情况（这样就不用改skip了）就写成`\\.`了，比如这可以正确匹配`"She said: \"Vimscript is tricky, but useful\"!"`，

### CH48 Basic Folding
1. 手动折叠，保存在内存中，关了就没了，你可以用`:mkview [1|2...]`来保存，用`:loadview [1|2...]`来载入，都保存在`~/.vim/view`中，参看`:h viewdir`
2. Marker折叠，这种是文本中带有`// {{{`和`// }}}`的会自动折叠，但比如在JS里`{`和`}`也会折叠
3. Diff折叠，这个只有在对比文件中才有用
4. Expr折叠，这是最强大的自定义折叠功能，但工作量也多，下章讲
5. Indent折叠，按缩写折叠，以及一些空行
6. 折叠快捷键
  - `zf[old]`是创建一个折叠
  - `zc[close]`是关闭所在光标折叠
  - `zo[pen]`是打开所在光标折叠
  - `zm[ore]`是进行一层折叠
  - `zr[educe]`是减少一层（即统一打开一层折叠）
  - 以上第二个字母都可以换成大写使用，表示为全部做某事
1. `foldlevel`大于这个的所有折叠将被折叠，如果是0就表示关闭所有折叠（相当于执行了`zM`)，`foldlevelstart`是当你打开一个新文件时的`foldlevel`
2. `foldminlines`表示折叠后至少要展示的行数，也就是说少于等于这个行数就不折叠了，如果你仍然要折叠，那会认为更大一段要折叠，比如一个缩进只有2行，这时`:set foldminlines=2`，那这2行死活是不会折叠的，如果你在两行中按`zc`，则会将周围的上一层缩进一起折叠了

### CH49 Advanced Folding
1. 折叠规则：
    - 每一行都有一个折叠层数，这是个是>=0的数
    - ==0的行是永远不会折叠的
    - 相邻折叠层数的行会被一起折叠
    - 如果一个层数X被折叠，则所有相邻大于等于X的行都会被折叠进来
1. 你可以用`:echo foldlevel(line_num)`来显示第几行的折叠层数
2. 有个技巧是，如果你自定义的一个foldlevel函数返回了`-1`，则会告诉vim这是未定义的折叠层数，vim会使用这行上面或下面的一行中**较小**的作为这行的foldlevel
3. 如果上面函数返回`>n`，就表示这是个大于n的折叠层数
3. 一般自己定义一个按Indent的层数函数可以这样写
    ```vim
    function! IndentLevel(lnum)
        return indent(a:lnum) / &shiftwidth
    endfunction
    ```

### CH50 Section Movement Theory
1. 这章讲了`[[`,`[]`,`][`,`]]`起源于`nroff`语言（一个类似Latex的文本语言）的宏
2. `[`和`]`分别是向前或向后寻找，第二位的`[`,`]`表示寻找`{`还是`}`，在C语言里就是跳到上（或下，取决于第一位是`[`还是`]`）一个函数的开始或结尾

### CH51 Potion Section Movement
1. 这章为Potion语言打造了一个自制的section跳转（实现`[[`,`[]`,`][`,`]]`），代码太多，直接看[原文](http://learnvimscriptthehardway.stevelosh.com/chapters/51.html)吧

### CH52 External Commands
1. 这章实现了一个自动编译的功能，新建`~/.vim/ftplugin/potion/running.vim`
    ```vim
    if !exists("g:potion_command")
        let g:potion_command = "potion"
    endif
    function! PotionCompileAndRunFile()
        silent !clear
        execute "!" . g:potion_command . " " . bufname("%")
    endfunction
    nnoremap <buffer> <localleader>r :call PotionCompileAndRunFile()<cr>
    ```
    这里需要设置`g:potion_command`的值
1. 介绍下`system(expr[, input])`函数，expr是命令，input是之后输入的内容，比如有的命令支持从stdin读取数据，input就是那里的内容
2. 给那些想用vim做任何事的人看`:h design-not`
3. `:read expr`是在当前光标下插入expr文件内容，`:read !expr`是插入执行命令的结果

### CH53 Autoloading
1. 对于一些小的插件，在载入时全部载入还是OK的，但如果比较大的就会花费一些时间，这时就要延迟载入，用`:call somefile#Hello()`，有了这个的函数，vim会从`~/.vim/autoload/somefile.vim`中找这个函数，如果有多个`#`，比如`path#a#b()`会从`~/.vim/autoload/path/a.vim`中找，然后多次调用不会重新载入这个文件，所以你作了修改也没用，但如果你调用`:call somefile#BadFunction()`，那就会重新载入了，并且`#Hello()`的更新也生效了
2. 一般会把map的函数以这种命名放在autoload里，这样只有第一次使用这个map时才会load这个文件
3. [本章](http://learnvimscriptthehardway.stevelosh.com/chapters/53.html)最终产物是potion 插件的自动载入，依然都是代码，自行查看原文

### CH54 Documentation
1. 每个插件都最好有个文档来说明，这个文件放在`~/.vim/doc/`下，与插件名同名的.txt 文件
2. 编辑完文件后，用`:Helptags`把这个文件加入索引，然后就可以用`:h xxx`来查看了
3. 你可以用[figlet](http://www.figlet.org/)来生成一个字符的立体画，非常酷炫
3. 哪些需要放在doc中说明呢
    - Introduction 这是放整个插件的概览
    - Usage 告诉用户应该怎么用，比如有哪些map，如果mapping太多，建议你单独开一个`Mappings`章节来放
    - Mappings 见上
    - Configuration 这里应该列出所有需要用户修改的值，及它的**效果**和**默认值**
    - License 只要包含license的url就行，千万别包含整个文本
    - Bugs 这里只记录主要的bugs，并且告诉用户怎么找到你报告bug
    - Contributing 如果你期望用户可以帮你修复bug，明确告诉用户他应当怎么做去修复bug，是发pull request？还是发邮件？
    - Changelog 记录版本X到版本Y的变化过程，十分建议你按照[Semantic Versioning](http://semver.org/)去定义你的版本
    - Credits 这里可以包含自己的名字，以及一些给你启发的脚本名，贡献者们
1. 帮助文档中，一排的`=`可以分隔章节，`-`分隔小章节，用`*xxx*`来生成tag，这样能被help索引到，用`|`包围的单词是一个跳转的链接，在这些词上按`<c-]>`可以跳到对应的tag上，用单引号`'`来表示一个选项名，用波浪号`~`放在一行结尾，如`Heading~`将会高亮整行，用`> xxxx \n yyyy <`表示一段代码，中间可以换行，还有些自动高亮的单词，如`Todo`,`Error`是`~/.vim/syntax/help.vim`下配置的
2. 有些好的例子可以参考下
    - [Clam](https://github.com/sjl/clam.vim/blob/master/doc/clam.txt) 一个简单的例子
    - [NERD_tree](https://github.com/scrooloose/nerdtree/blob/master/doc/NERD_tree.txt) 观察它如何组织mapping
    - [Surround](https://github.com/tpope/vim-surround/blob/master/doc/surround.txt)
    - [Splice](https://github.com/sjl/splice.vim/blob/master/doc/splice.txt) 这里用了ASCII画的形式来描述
1. 可以使用`:left`,`:center`,`:right`来达到左中右对齐的效果

### CH55 Distribution
1. 将你的插件放在网上，比如[the scripts section of the Vim websit](http://www.vim.org/scripts/)，但现在大多放在GitHub上，也方便使用Pathogen管理
2. 关注reddit上的[/r/vim](http://www.reddit.com/r/vim/)版块

### CH56 What Now?
以下内容在你闲得蛋疼可以看（但作为译者我保证每次看完你都会有所收获）

- `:h highlight` 你可以发现一些内置的配色方案，可以用在之后的插件中
- `:h user-commands` 学习怎样创建一个你自己的Ex命令，类似`:command`
- `:h ins-completion` 这就是插入模式下的自动补全啊，进阶阅读`:h omnifunc`和`:h compl-omni`（这里原作者打成`:h coml-omni`了）
- `:h quickfix.txt` vim还可以和编译器进一步地互动，阅读这个吧
- `:h Python` `:h Ruby` `:h Lua` vim居然还支持这些语言的接口
- 以下是些更有趣的内容
    - `:help various-motions`
    - `:help sign-support`
    - `:help virtualedit`
    - `:help map-alt-keys`
    - `:help error-messages`
    - `:help development`
    - `:help tips`
    - `:help 24.8`
    - `:help 24.9`
    - `:help usr_12.txt`
    - `:help usr_26.txt`
    - `:help usr_32.txt`
    - `:help usr_42.txt`


非常感谢GB大牛推荐我阅读这本书！
