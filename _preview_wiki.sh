#!/bin/bash
export LC_ALL=en_US.UTF-8
export LC_CTYPE=UTF-8
ROOT_DIR=$(dirname $0)
cd $ROOT_DIR/_wiki && simiki generate && simiki p -w
