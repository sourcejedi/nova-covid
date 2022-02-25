#!/bin/sh
set -e

dir=out/changes/
mkdir -p "$dir"

head -q -n1 download-zoe/incidence/incidence_*.csv |
    uniq -c \
    > "$dir"/old_head_incidence

head -q -n1 download-zoe/prevalence_history/prevalence_history_*.csv |
    uniq -c \
    > "$dir"/old_head_prevalence_history
