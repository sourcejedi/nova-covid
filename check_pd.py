#!/usr/bin/env python3
import csv
import mmap
from collections import namedtuple
from pathlib import Path

# FIXME: it's not very helpful to just show a backtrace when a check fails.
# And... don't assume this particular program is Quality.  I'm using it, feel
# free to run it, but don't trust.  Verify.

MapRow = namedtuple('MapRow', ('respondent', 'population', 'active_cases', 'percent'))

def check_prevalence_digest(official_file, check_file):
    official = {}
    o_csv = csv.DictReader(official_file)
    for row in o_csv:
        utla = row['UTLA19CD']

        population_float = float(row['population'])
        population = int(population_float)
        assert population == population_float

        percent_str = row['percentage']
        if percent_str == '':
            percent = None
        else:
            percent = float(percent_str)

        row = MapRow(
            int(row['respondent']),
            population,
            float(row['active_cases']),
            percent)
        official[utla] = row

    # You *could* do this efficiently
    # without mmap, but why bother?
    def reversed_lines(infile):
        data = mmap.mmap(infile.fileno(), 0, prot=mmap.PROT_READ)
        j = len(data)
        i = data.rfind(b'\n', 0, j)
        yield data[i+1:j].decode('ascii')
        while i >= 0:
            j = i
            i = data.rfind(b'\n', 0, j)
            yield data[i+1:j+1].decode('ascii')
    def reversed_lines1(infile):
        # header line
        buf = next(infile)
        # yield header line + reversed lines, without repeating header line
        for line in reversed_lines(infile):
            yield buf
            buf = line

    c_csv = csv.DictReader(reversed_lines1(check_file))
    last_date = None
    for row in c_csv:
        date = row['date']
        if last_date == None:
            last_date = date
        if date != last_date:
            continue
        date_prev = date

        utla = row['UTLA19CD']
        official_row = official[utla]

        population_float = float(row['population'])
        population = int(population_float)
        assert population == population_float
        assert population == official_row.population

        respondent_count = float(row['respondent_count'])
        assert round(respondent_count) == official_row.respondent

        # Looks like the threshold for 'Not enough contributors' is 750.
        #
        # Detail: the threshold is applied *before* respondent_count is
        # rounded to a whole number.  respondent_count can be fractional
        # because the map is based on a rolling average.
        assert (official_row.percent == None) == (respondent_count < 750)

        corrected_covid_positive = float(row['corrected_covid_positive'])
        assert abs(corrected_covid_positive - official_row.active_cases) < 1e-8


official_dir = Path('download/utla_prevalence_map/')

# I haven't run prevalence_digest for all dates.
# The input files are big and it takes time.
indir = Path('out/prevalence_digest/')
prefix = 'corrected_prevalence_region_trend_'
paths = list(indir.glob(prefix + '*/'))
paths.sort()
for path in paths:
    date = path.name[len(prefix):]
    official_path = official_dir / f'utla_prevalence_map_{date}.csv'

    check_path = path / 'utla_8d_average.csv'
    print(check_path)
    with (official_path.open() as official_file,
          check_path.open() as check_file):
        check_prevalence_digest(official_file, check_file)
