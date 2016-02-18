---
title: "vim"
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
