#!/usr/bin/env python3
import os
import mmap
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
            f = open(self.path + '/' + region + '.csv', 'w', newline='')
            csv_writer = csv.writer(f)
            csv_writer.writerow(self.fieldnames)

            self.writers[region] = Writer(f, csv_writer)
        return self.writers[region].csv


def split_region_csv(infile, out_path):
    reader = csv.DictReader(infile)

    os.makedirs(out_path, exist_ok=True)
    with Writers(out_path, reader.fieldnames) as writers:
        for row in reader:
            region = row['region']
            writers.get(region).writerow(row.values())

def split_region(in_path, out_path):
    indir = Path(in_path)
    paths = list(indir.glob('*.csv'))
    paths.sort()
    assert(paths)
    with paths[-1].open() as csvfile_in:
        split_region_csv(csvfile_in, out_path)


def _publish_date(paths, writers):
    date_field = writers.fieldnames.index('date')
    region_field = writers.fieldnames.index('region')

    for path in paths:
        with path.open('rb') as infile:
            # You *could* do this efficiently
            # without mmap, but why bother?
            def reversed_lines():
                data = mmap.mmap(infile.fileno(), 0, prot=mmap.PROT_READ)
                j = len(data)
                i = data.rfind(b'\n', 0, j-1)
                yield data[i+1:j]
                while i >= 0:
                    j = i
                    i = data.rfind(b'\n', 0, j)
                    yield data[i+1:j+1]

            lines = reversed_lines()

            prev_date = None
            for line in lines:
                line = line.decode('us-ascii')
                line = line.strip()
                row = line.split(',')
                date = row[date_field]
                if prev_date is not None and date != prev_date:
                    break
                prev_date = date
                region = row[region_field]
                # DictWriter
                writers.get(region).writerow(row)

def publish_date(in_path, prefix, out_path):
    os.makedirs(out_path, exist_ok=True)

    indir = Path(in_path)
    paths = list(indir.glob(prefix + '*.csv'))
    paths.sort()

    # Use all files after method change v5
    paths = [path for path in paths if path.name[len(prefix):] >= '20211003.csv']
    assert paths

    # Header line
    with paths[0].open('r') as infile:
        header = infile.readline()
        header = header.strip()
        fieldnames = header.split(',')

    with Writers(out_path, fieldnames) as writers:
        _publish_date(paths, writers)


def main():
    publish_date('download/incidence/', 'incidence_', 'out/publish-date.incidence.region')
    split_region('download/incidence/', 'out/latest_incidence.region')
    split_region('download/prevalence_history/', 'out/latest_prevalence_history.region')

if __name__ == '__main__':
    main()
