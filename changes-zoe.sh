#!/bin/sh
set -e

dir=out/changes/
mkdir -p "$dir"

head -q -n1 download-zoe/incidence/incidence_*.csv |
    uniq -c \
    > "$dir"/head
