---
layout: post
title: "learn vim script the hard way 笔记（下）"
description: ""
category: note
comments: true
tags: []
---
{% include JB/setup %}

[上一篇](/2017/06/learn-vim-script-the-hard-way-b.html)

### CH31 Basic Regular Expressions
1. `/`和`?`，前者向后找，后者向前找

### CH32 Case Study: Grep Operator, Part One
1. `:nnoremap <leader>g :grep -R <cWORD> .<cr>`可以搜索`<cWORD>`，表示光标下的单词（包括连字符，比`<cword>`更大），之后可以用`:cwindow`查看`quickfix`窗口
2. 以上还有一点要修改，如果光标在一个`foo;ls`下，使用后实际会执行`ls`命令，原理和SQL注入类似，所以需要用单引号保证字面值，`:nnoremap <leader>g :grep -R '<cWORD>' .<cr>`
3. 但上面对于光标有单引号的不启作用，用`:echom shellescape(expand("<cWORD>"))`可以显示shellescape后的值
4. 最终版本`:nnoremap <leader>g :silent execute "grep! -R " . shellescape(expand("<cWORD>")) . " ."<cr>:copen<cr>` ，前面加个`:silent`可以防止搜索时的输出，最后再`:copen`打开结果页

### CH33 Case Study: Grep Operator, Part Two
进入.vim/plugin/下，新建一个文件"grep-operator.vim"，写上`nnoremap <leader>g :set operatorfunc=GrepOperator<cr>g@`和`function! GrepOperator(type) | echom "Test" | endfunction`，这时用`<leader>giw`会发现打出了`Test`
<!--more-->

1. 这里函数名后面有个`g@`，表示这是个`operatorfunc`，就是说后面可以跟动作，比如`iw`表示光标所在的单词，`i(`表示光标所在的圆括号，`g@`后可以跟`line`,`char`,`block`表示动作类型，这个也体现在上面函数的参数`type`上
2. 再给visual模式加个命令，加上`vnoremap <leader>g :<c-u>call GrepOperator(visualmode())<cr>`，解释下这个`<c-u>`，和shell中的`<c-u>`一样删除光标前内容直到行首，如果进入选择模式后，这时按`:`，会发现命令行自带了`:'<,'>`，这时如果按`<c-u>`就会“删掉从光标位置到开头的内容”，只剩`:`，正是我们想要的，这里的参数`visualmode()`是表示进的哪种visual模式，比如字节型就是`v`，行选择就是`V`，块选择就是`<c-v>`
3. 上面把函数体改成`echom a:type`后，会有几种情况，`viw<leader>g`显示`v`，`vjj<leader>g`显示`V`，`<leader>gviw`显示`char`，`<leader>gG`显示`line`

### CH34 Case Study: Grep Operator, Part Three
1. 一个可用的思路是，将选中的内容复制到临时寄存器中，但记得最后还原，如
    ```sh
    let saved_unnamed_register = @@
    # do something
    let @@ = saved_unnamed_register
    ```
1. 当你真正要写一个vim脚本时，最好使用命名空间，之前的函数改为`nnoremap <leader>g :set operatorfunc=<SID>GrepOperator<cr>g@`，这时函数名前加了`<SID>`，同时，函数定义改为`function! s:GrepOperator(type)`
2. `<SID>`应该相当于是Script ID，加上这个会在执行的时候替换为`<SNR>12_func`这种形式，另外在脚本内部使用时，前面加`s:`即可，但如果是一个map外部调用，应该使用`<SID>`

### CH35 Lists
1. vim的list下标是从0开始，用-1表示最后一个元素，-2表示倒数第二个
2. 使用`l[0:2]`表示切片，这里注意是表示从第0个到第2个元素（闭区间），支持`[-2:-1]`写法，如果下界大于上界则显示空list
3. 字符串也可以进行list的操作，但要注意`"abcd"[-2]`这种只用一个负数的操作会显示为空字符串，而用`"abcd"[-2:]`才能显示为"cd"
4. `add(['a'], 'b')`将`b`插入末尾，注意这些命令在normal模式下用要写成`:call add(xxx)`
5. `extend(list, [1,2])`将两个list合成一个
5. `len(list)`求长度
6. `get(list, 0, 'default')`取list[0]，如果不存在则返回"default"
7. `index(list, 'a')`返回a在list中第一次出现的位置，没有返回-1
8. `join(list, glue)`类似php的`implode`，将list用glue连接成字符串
9. `reverse(list)`**就地**倒排list
10. `unlet list[3:]`删除list的3到最后
11. `:let l = remove(list, 3, -1)`返回删完的list
12. `filter(list, 'v:val !~ "x"')`移除元素中带`x`的，后面表达式为真将被留下
10. list用`+`号连接，也可以`+=`
11. 直接写`b = a`相当于b是a的引用，对a操作同时也会作用于b，复制可以用`b = copy(a)`，或者`b = a[:]`，但是上面这个只对一维有效，如果`a[0][1] = 'aa'`，这时会发现b[0]也变了，深度复制用`b = deepcopy(a)`（最多能复制100层）
12. 用`:echo a is b`来判断是不是同一个list，而`a == b`是从值上比较的，有个例外是，`:echo 4 == "4"`显示是1，而`:echo [4] == ["4"]`显示是0
13. 支持分别赋值，如`:let [var1, var2] = list`，如果只需要前几个值，可以这样`:let [var1, var2; rest] = mylist`，这里rest一定要有，否则会报错
14. 使用`for item in mylist`进行循环，如果是多层，则用`for [lnum, col] in [[1, 3], [2, 8], [3, 0]]`，后面的list必须每项个数一致

### CH36 Looping
1. for循环像这样
    ```sh
    :for i in [1,2,3,4]
    :  let c += i
    :endfor
    ```
1. while循环像这样
    ```sh
    :while c <= 4
    :  let total += c
    :  let c += 1
    :endwhile
    ```
1. 有点要注意的是，当`for i in mylist`时，在对当前元素执行命令前，vim会保存下一个的引用，所以这时即使删除mylist的当前元素也是OK的，但删除之后的元素会导致vim找不到它

### CH37 Dictionaries
1. `:echo {'a': 1, 100: 'foo',}`这是定义一个字典，同时最好保留后面的逗号，防止在多行时出错
2. vim的字典只能是字符串，写成数字也会被转成字符串
3. 还可以用`:echo {}.a`的形式
4. 用`remove(dict, 'a')`或`unlet(dict.b)`来删除元素，十分推荐用`remove`，因为它的作用比`unlet`大
5. 可以用`:for key in keys(mydict)`来循环得到key值，同理，`:for v in values(mydict)`循环value，还可以`:for [key, value] in items(mydict)`两个都循环
6. 可以用`has_key()`验证一个key是不是在字典中
7. 字典的函数和上面list的函数类似

### CH38 Toggling
1. 之前学过用`:setlocal nu!`是可以开头某个布尔值的，下面来看下对于非布尔怎么做
2. 比如可以检测值满足某个条件A时，设为x，满足条件B时，设为y这样，例如
    ```sh
    nnoremap <leader>f :call FoldColumnToggle()<cr>
    function! FoldColumnToggle()
        if &foldcolumn
            setlocal foldcolumn=0
        else
            setlocal foldcolumn=4
        endif
    endfunction
    ```
1. 或者打开或关闭某个窗口，如`:copen`和`:cclose`，这时可以用全局变量标识
    ```sh
    nnoremap <leader>q :call QuickfixToggle()<cr>
    function! QuickfixToggle()
        if g:quickfix_is_open
            cclose
            let g:quickfix_is_open = 0
        else
            copen
            let g:quickfix_is_open = 1
        endif
    endfunction
    ```
    这里只有一点不太完美，如果用户手动打开了窗口，则全局变量是不会更新的，但这里要花大工夫来完成，得不偿失
1. 这里还有一点是在打开多个文件再使用`<leader>q`时，如果在quick-fix窗口中使用，则会返回上一个split的窗口，而不是之前`copen`时所在的窗口，所以要做以下修改，同时这也是个约定俗成的写法
    ```sh
    nnoremap <leader>q :call QuickfixToggle()<cr>
    let g:quickfix_is_open = 0
    function! QuickfixToggle()
        if g:quickfix_is_open
            cclose
            let g:quickfix_is_open = 0
            execute g:quickfix_return_to_window . "wincmd w"
        else
            let g:quickfix_return_to_window = winnr()
            copen
            let g:quickfix_is_open = 1
        endif
    endfunction
    ```


### CH39 Functional Programming
1. 就是你可以把变量赋成函数，然后变量名就相当于函数名去调用，这里要注意一点是，变量可以不像函数名那样遵守首字母大写的约定，如
    ```sh
    :let funcs = [function("Append"), function("Pop")]
    :echo funcs[1](['a', 'b', 'c'], 1)
    ```
1. 再来感受一个类似py中的map的例子
    ```sh
    function! Mapped(fn, l)
        let new_list = deepcopy(a:l)
        call map(new_list, string(a:fn) . '(v:val)')
        return new_list
    endfunction
    ```
相当于对l数组中的所有元素过一遍函数fn

### CH40 Paths
1. 为啥这章和上章函数式编程没有一点关系了……
2. 获取绝对路径，`:echom expand('%:p')`或`:echom fnamemodify('foo.txt', ':p')`，但第二个必须手写foo.txt（可以是个不存在的文件）
3. 列出当前文件夹下的文件`:echo globpath('.', '*')`，还可以递归地显示文件`:echo split(globpath('.', '**'), '\n')`，递归地查找某个文件`:echo split(globpath('.', '**/*.py'), '\n')`
4. `expand(expr[, nosuf[, list]])`，expr可以以
    - `%` 当前文件
    - `#` 另一个文件
    - `#n` 另n个文件

    后面还可以接修饰符
    - `:p` 扩展成全路径
    - `:h` 会把最后一部分去掉（这个可以接在一些修饰符后面，比如':p:h'就相当于全路径的文件夹名，如果只用':h'可能只显示'.'）
    - `:t` 只保留路径最后一部分
    - `:r` 移除扩展名的全路径
    - `:e` 文件扩展名
1. `simplify(filename)` 尽可能简化路径，会把`.././/`这种简化掉，快捷方式或链接不解析
2. `resolve(filename)` 可以解析快捷方式或链接，并返回简化后的全路径
3. 关于通配符，可以有`?`,`*`,`**`,`[abc]`，这里注意在win下比较蛋疼，如果要实际匹配字面值`path[abc]`写`path\[abc]`会认为反斜杠是目录分隔符，避免这样，可以写成`path\[[]abc]`
