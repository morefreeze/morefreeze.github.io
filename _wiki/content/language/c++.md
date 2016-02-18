---
title: "C++"
date: 2016-01-18 20:29
---

[TOC][]()

# Data structure

## Heap

### include

    #include <queue>

### Small root heap

    priority_queue<int, vector<int>, std::greater<int> > h;

### Custom compare function 1

    struct Node{
        int x, y;
        Node(int a = 0, int b = 0 ):
            x(a), y(b) {}
    };

    bool operator<(const Node &a, const Node &b){
        if(a.x == b.x) return a.y> b.y;
        return a.x > b.x;
    }

    // priority_queue<Node> q;

### Custom compare function 2

    struct Node{
        int x, y;
        Node(int a = 0, int b = 0 ):
            x(a), y(b) {}
    };

    struct cmp{
        bool operator() (Node &a, Node &b){
            if(a.x == b.x) return a.y> b.y;
            return a.x> b.x;.
        }
    };

    // priority_queue<Node, vecotr<Node>, cmp> q;
