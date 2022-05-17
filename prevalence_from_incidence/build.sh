#!/bin/sh

# Debug mode
set -o xtrace

# Find our base directory
if [ -e ../prevalence_from_incidence/build.sh ]; then
    cd ..
elif [ -e ./prevalence_from_incidence/build.sh ]; then
    cd .
else
    echo "Usage: ./prevalence_from_incidence/build.sh"
    exit 1
fi &&

out=./out/prevalence_from_incidence/ &&
mkdir -p "$out" &&

# Prevalence time series: sum of England regions
ph=./out/prevalence_history.England/prevalence_history_20210209.csv &&
if [ ! -e "$ph" ]; then
    ./prevalence.England.py
fi &&
cp "$ph" "$out" &&

# Incidence time series:
i=./download/incidence/incidence_20210205.csv &&
i_h=./download/incidence_history/incidence_history_20210209.csv &&
# Sum of England regions
./incidence.England.py < "$i" > "$out"/incidence_20210205.England.csv &&
./incidence.England.py < "$i_h" > "$out"/incidence_history_20210209.England.csv &&
# England as one unit, no region-weighting
grep ,England, < "$i" > "$out"/incidence_20210205.unweighted.csv &&

# Prevalence from incidence conversion:
./prevalence_from_incidence/prevalence.py \
    < "$out"/incidence_20210205.England.csv \
    > "$out"/prevalence_from_incidence_20210205.England.csv &&
# conversion from Lancet paper figure 2
./prevalence_from_incidence/prevalence.py \
    --use-gamma \
    < "$out"/incidence_20210205.England.csv \
    > "$out"/prevalence_from_incidence_20210205.gamma.csv &&
# conversion from Lancet paper figure 2,
# run on England as one unit, without region-weighting.
./prevalence_from_incidence/prevalence.py \
    --use-gamma \
    England \
    < "$i" \
    > "$out"/prevalence_from_incidence_20210205.uweighted.gamma.csv &&

exit 0
