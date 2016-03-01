#!/bin/bash
ROOT_DIR=$(dirname $0)
cd $ROOT_DIR/_wiki && simiki generate && simiki p -w
