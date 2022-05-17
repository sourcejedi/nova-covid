#!/bin/sh

# Debug mode
set -o xtrace

# Download ZOE files using gsutil from google-cloud-sdk.
# See https://sourcejedi.github.io/2022/01/31/zoe-covid-study.html
get() (
    get="$1" &&
    dir="download/$2" &&

    mkdir -p "$dir" &&
    cd "$dir" &&
    gsutil -m cp -n "$get" .
)

get 'gs://covid-public-data/csv/incidence_202*.csv' \
        'incidence/' &&
get 'gs://covid-public-data/csv/RevisedStats/prevalence_history_202*.csv' \
        'prevalence_history/' &&
get 'gs://covid-public-data/csv/RevisedStats/incidence_history_202*.csv' \
        'incidence_history/' &&

exit 0
