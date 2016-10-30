---
title: "Vim"
date: 2016-02-18 11:43
---

[TOC][]()

## Move in document
- `gj` move down display line, if `:set wrap` and one line split into lines, this move will be downward to display instead of line number+1. Try it.

## Motion in document

- Use `d{motion}`, `y{motion}` and so on. `{motion}` can be following:
    - `iw` current [word][1](`:h word` see detail)
    - `aw` current word and a space
    - `iW` current [WORD][2]
    - `aW` current WORD and a space
    - `is` current sentence
    - `as` current sentence and a space
    - `ip` current paragraph
    - `iP` current paragraph and a space

- Use these as memory shortcut:
    - `i`nside
    - `a`round
    - `w`ord
    - `s`entence
    - `p`aragraph


[1]: #word "word is combined with alphabet, number, underscore, other non-spacing char. e.g.: `e.g.` which are four words."
[2]: #WORD "WORD is splited with space."

## Register

- `"{register}"` use with register, following is some registers(`:h registers`):
    - `""` unnamed register, use `x`, `d` will cut content into this
    - `"_` black hole, like `/dev/null`
    - `"+` system clipboard, like `ctrl-c`, then use `"+y` will paste content in vim

- `q{register}q` will clear a register content

## Dance with Command

1. `q:` open command window when normal mode, you can edit history of command or re-reun it while press `<CR>`
1. `<c-f>` open command window when command mode
1. If you need copy current word under cursor when command mode, press `<c-r><c-w>`. `<c-r><c-a>` for whole [WORD][2]
1. Consider below situation:

    You want to replace something with regex, but you may need construct regex many times, and then use `:s/regex/replace/g`

    Here is solution:

    1.  Use `/regex1` to match and see the result
    2.  The result is not what I want, change it with `/regex2`
    3.  You can use `q/` to find command history, repeat step 2-3 until perfect match
    4.  `:%s//replace/g`. if pattern is omit it will use last match.

## Insert datetime

    `strftime("%Y%m%d", localtime())`  # Notice anti-quote

# Code snippets

## beancount

### Date shorthand
```
snippet dt "date YYYY-mm-dd"
	${3:`strftime("%Y")`}-${2:`strftime("%m")`}-${1:`strftime("%d")`} 
```

### Add balance
This will add a `balance` for an account and auto `pad` it.
```
snippet bal
	${9:`strftime("%Y", localtime()-86400)`}-${8:`strftime("%m", localtime()-86400)`}-${7:`strftime("%d", localtime()-86400)`} pad $2 ${3:Equity:Opening-Balances}
	${6:`strftime("%Y")`}-${5:`strftime("%m")`}-${4:`strftime("%d")`} balance ${2:Assets:Cash}               ${1} CNY
```

### Add note
```
snippet note
	${9:`strftime("%Y")`}-${8:`strftime("%m")`}-${7:`strftime("%d")`} note ${3:Assets:Cash} "${1} ${2} CNY"
```

### Add query
```
snippet query
	${9:`strftime("%Y")`}-${8:`strftime("%m")`}-${7:`strftime("%d")`} query "${1}" "
				SELECT ${2} WHERE ${3}
	"
```

### General transaction
```
snippet new
	${7:`strftime("%Y")`}-${6:`strftime("%m")`}-${5:`strftime("%d")`} * "${1}"
				${2:Assets:Cash}            -${3} CNY
				${4}
```

### House rent
This records house rent monthly.
```
snippet house "house rent"
	${8:`strftime("%Y")`}-${7:`strftime("%m")`}-${6:`strftime("%d")`} * "House rent ${9:`strftime("%Y/%m", localtime()-86400*30)`}"
				Assets:Alipay:YuE                       -3000 CNY
				Assets:Big:House
```

### Car installment
This records a car installment and you can record this is which period. You need replace `$Bank` to your bank.
```
snippet car "car installment"
	${4:`strftime("%Y")`}-${3:`strftime("%m")`}-${2:`strftime("%d")`} * "Car amortization ${1}/24"
				Liabilities:$Bank:CreditCard         -2000.00 CNY
				Assets:Big:Car
```

### Salary
This is my salary template, it including social insurance and income tax,
you need change `$Company` to your company name and `$Bank` as same. `Vacation` is your loss because personal leave.
```
snippet sal "salary"
	${8:`strftime("%Y", localtime()-86400)`}-${7:`strftime("%m", localtime()-86400)`}-${6:`strftime("%d", localtime()-86400)`} * "${9:`strftime("%Y/%m", localtime()-86400*30)`} salary"
				Income:$Company:Salary              -${1:10000} CNY
				Expenses:Government:SocialInsurance ${2} CNY
				Expenses:Government:HouseFund       ${3} CNY
				Expenses:Government:IncomeTax       ${4} CNY
				Expenses:$Company:Vacation          ${5:0} CNY
				Assets:$Bank:Saving
```
