#!/bin/sh

# Debug mode
set -o xtrace

dates="202[2-9]*"
if [ ! -e download/lad_prevalence_map/lad_prevalence_map_20211231.csv ]; then
   dates="202*"
fi

# Download ZOE files using gsutil from google-cloud-sdk.
# See https://sourcejedi.github.io/2022/01/31/zoe-covid-study.html
get() (
    get="$1" &&
    dir="download/$2" &&

    mkdir -p "$dir" &&
    cd "$dir" &&
    gsutil -m cp -n "$get" .
)

get "gs://covid-public-data/csv/incidence_${dates}.csv" \
        'incidence/' &&
get "gs://covid-public-data/csv/RevisedStats/prevalence_history_${dates}.csv" \
        'prevalence_history/' &&
get "gs://covid-public-data/csv/RevisedStats/incidence_history_${dates}.csv" \
        'incidence_history/' &&
get "gs://covid-public-data/csv/utla_prevalence_map_${dates}.csv" \
        'utla_prevalence_map/' &&
get "gs://covid-public-data/csv/lad_prevalence_map_${dates}.csv" \
        'lad_prevalence_map/' &&

get "gs://terraform-covid-website-data-prod/personalized_assets/backup_files/newly_sick_table_${dates}.csv" \
        'newly_sick_table/' &&

exit 0
