#!/bin/sh
set -o errexit

dir=out/tail/
mkdir -p "$dir"

file="$dir"/incidence_history.csv
headfile="$(ls download/incidence_history/*.csv | head -n1)"
head -n1 "$headfile" > "$file"
for i in download/incidence_history/*.csv; do
    grep ",England," "$i" | tail -q -n1  >> "$file"
done

file="$dir"/prevalence_history.csv
headfile="$(ls out/prevalence_history.England_weighted/*.csv | head -n1)"
head -n1 "$headfile" > "$file"
for i in out/prevalence_history.England_weighted/*.csv; do
    tail -q -n1 "$i" >> "$file"
done

# incidence files change format half-way through
# see incidence.std_form.py
file="$dir"/incidence.std_form.csv
headfile="$(ls out/incidence.std_form/*.csv | head -n1)"
head -n1 "$headfile" > "$file"
for i in out/incidence.std_form/*.csv; do
    tail -q -n1 "$i" >> "$file"
done
