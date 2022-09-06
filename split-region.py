#!/usr/bin/env python3
import os
import csv
from pathlib import Path
from collections import namedtuple

Writer = namedtuple('Writer', ('file', 'csv'))

class Writers:
    def __init__(self, path, fieldnames):
        self.path = path
        self.fieldnames = fieldnames
        self.writers = {}

    def __enter__(self):
        return self

    def __exit__(self, *_):
        for (f, _) in self.writers.values():
            f.close()
        self.writers.clear()

    def get(self, region):
        if region not in self.writers:
            f = open(self.path + '/' + region + '.csv', 'w')
            csv_writer = csv.DictWriter(f, self.fieldnames)
            csv_writer.writeheader()

            self.writers[region] = Writer(f, csv_writer)
        return self.writers[region].csv


def split_region_csv(infile, out_path):
    reader = csv.DictReader(infile)

    os.makedirs(out_path, exist_ok=True)
    with Writers(out_path, reader.fieldnames) as writers:
        for row in reader:
            region = row['region']
            writers.get(region).writerow(row)

def split_region(in_path, out_path):
    indir = Path(in_path)
    paths = list(indir.glob('*.csv'))
    paths.sort()
    assert(paths)
    with paths[-1].open() as csvfile_in:
        split_region_csv(csvfile_in, out_path)

split_region('download/incidence/', 'out/latest_incidence.region')
split_region('download/prevalence_history/', 'out/latest_prevalence_history.region')
