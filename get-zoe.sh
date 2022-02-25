#!/bin/sh

# debug
set -o xtrace

# gsutil from google-cloud-sdk

get() (
    get="$1" &&
    dir="download-zoe/$2" &&

    mkdir -p "$dir" &&
    cd "$dir" &&
    gsutil -m cp -n "$get" .
)

get 'gs://covid-public-data/csv/incidence_202*.csv' 'incidence/' &&
get 'gs://covid-public-data/csv/RevisedStats/prevalence_history_202*.csv' \
        'prevalence_history/'
