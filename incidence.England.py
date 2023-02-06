#!/usr/bin/python3
import sys
import csv

def england(file_in, file_out):
    england = dict()

    csv_in = csv.DictReader(file_in)
    for row in csv_in:
        # Note: input file will already include England.
        # However we output the sum of English regions;
        # in some versions of ZOE this will be different.
        if row['region'] in ['England', 'Wales', 'Scotland', 'Northern Ireland', 'UK']:
            continue
        date = row['date']
        incidence = float(row.get('pop_mid') or row.get('covid_in_pop'))
        england[date] = england.get(date, 0) + incidence

    csv_out = csv.writer(file_out)
    csv_out.writerow(['date', 'covid_in_pop'])
    dates = sorted(england.keys())
    for date in dates:
        csv_out.writerow([date, england[date]])

if len(sys.argv) != 1:
    sys.exit("Usage: incidence.England.py < input.csv > output.csv")
file_in = sys.stdin
file_out = sys.stdout
england(file_in, file_out)
