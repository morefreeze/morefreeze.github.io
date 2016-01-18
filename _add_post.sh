#!/usr/bin/env bash
post_name=$(rake post title="$@" | tee /tmp/rake_log)
post_name=$(echo $post_name | awk 'NR==FNR {print $NF}')
vim $post_name
