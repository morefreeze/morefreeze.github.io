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

# Algorithm

## Binary Search

```c++
#include <iostream>
#include <vector>

int binary_search(std::vector<int> &v, int x){
    int left = 0;
    int right = int(v.size());
    int mid = (left+right) >> 1;
    while (left <= right) {
        if (v[mid] == x) {
            return mid;
        } else if (v[mid] < x) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
        mid = (left+right) >> 1;
    }
    return -1;
}

int main(int argc, char *argv[]) {
    std::vector<int> v;
    for (int i = 0; i < 10; ++i) {
        v.push_back(i);
    }
    for (int i = -1; i < 11; ++i) {
        std::cout << binary_search(v, i) << std::endl;
    }
    return 0;
}
```
