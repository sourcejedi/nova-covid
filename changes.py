#!/usr/bin/env python3

# This is starting to get a bit fragile.
# I.e. it would benefit from having tests.

import os
from pathlib import Path
import csv
import datetime


def changes_table(indir, prefix, outfile):
    paths = list(indir.glob(prefix + '*.csv'))
    paths.sort()
    prefix_len = len(prefix)

    prev_head = None
    prev_fields = None
    prev_regions = None
    for path in paths:
        print(path)
        name = path.name[prefix_len:-4]
        with path.open() as f:
            head = f.readline()
            assert head
            head = head.rstrip()
            assert head
            f.seek(0)

            read = csv.DictReader(f)
            fields = read.fieldnames
            assert fields
            row = next(read, None)
            assert row
            f.seek(0)

            regions = []
            read = csv.DictReader(f)
            row = next(read, None)
            assert row
            while row:
                region = row.get('region') or row.get('nhser19nm')
                assert region
                assert region not in regions
                regions.append(region)
                row = next(read, None)
            regions.sort()
            regions_set = set(regions)
            f.seek(0)

            assert f.readline().rstrip() == head
            heads = head.split(',')

        change = False
        if fields != prev_fields:
            display_fields = [field.replace('\n', ' ') for field in fields]
            outfile.write(f'{name}:  Fields:        {", ".join(display_fields)}\n')
            change = True
        if fields == prev_fields and head != prev_head:
            outfile.write(f'{name}:  Old headers:   {head}\n')
            outfile.write(f'{name}:  New headers:   {head}\n')
            change = True
        if regions != prev_regions:
            outfile.write(f'{name}:  Regions:       {", ".join(regions)}\n')
            change = True
        prev_fields = fields
        prev_head = head
        prev_regions = regions
        if change:
            outfile.write('\n')

    outfile.write(f'{name}\n')

def changes(indir, prefix, outfile):
    paths = list(indir.glob(prefix + '*.csv'))
    paths.sort()
    prefix_len = len(prefix)

    prev_head = None
    prev_fields = None
    prev_start = None
    prev_regions = None
    prev_offset = None
    prev_uk_maybe_weighted = None
    prev_en_maybe_weighted = None
    for path in paths:
        print(path)
        name = path.name[prefix_len:-4]
        with path.open() as f:
            head = f.readline()
            assert head
            head = head.rstrip()
            assert head
            f.seek(0)

            read = csv.DictReader(f)
            fields = read.fieldnames
            assert fields
            row = next(read, None)
            assert row
            start = row.get('date')
            assert start
            f.seek(0)

            regions = []
            read = csv.DictReader(f)
            row = next(read, None)
            assert row
            date = row.get('date')
            assert(date)
            while date == start:
                region = row.get('region')
                assert region
                assert region not in regions
                regions.append(region)
                row = next(read, None)
                assert row
                date = row.get('date')
            regions.sort()
            regions_set = set(regions)
            f.seek(0)

            read = csv.DictReader(f)
            mid_field = 'pop_mid'
            if mid_field not in fields:
                mid_field = 'covid_in_pop'
            if mid_field not in fields:
                mid_field = 'active_cases'

            if 'UK' in regions or 'England' in regions:
                uk_maybe_weighted = True
                en_maybe_weighted = True

                uk_mid = 0
                en_mid = 0
                file_uk_mid = 0
                file_en_mid = 0

                row = next(read, None)
                assert row
                date = row.get('date')
                assert(date)
                while date == start:
                    mid = row.get(mid_field)
                    assert mid
                    mid = float(mid)
                    region = row.get('region')
                    assert region
                    if region == 'UK':
                        file_uk_mid = mid
                    elif region == 'England':
                        file_en_mid = mid
                        uk_mid += mid
                    else:
                        if region in ['Wales', 'Scotland', 'Northern Ireland']:
                            uk_mid += mid
                        else:
                            en_mid += mid

                    row = next(read, None)
                    assert row
                    date = row.get('date')

                if abs(file_en_mid - en_mid) > 0.01:
                    en_maybe_weighted = False
                if abs(file_uk_mid - uk_mid) > 0.01:
                    uk_maybe_weighted = False

            if 'UK' not in regions:
                uk_maybe_weighted = None
            if 'England' not in regions:
                en_maybe_weighted = None
            f.seek(0)

            assert f.readline().rstrip() == head
            heads = head.split(',')
            date_field = 0
            if not heads[0]:
                date_field = 1
            assert heads[date_field] == 'date'

            # Optimized inner loop :)
            for line in f:
                pass
            date = line.split(',', 1 + date_field)[date_field]

            last_date = date
            last_date = last_date.split('-')
            last_date = map(int, last_date)
            last_date = datetime.date(*last_date)
            name_date = [name[:-4], name[-4:-2], name[-2:]]
            name_date = map(int, name_date)
            name_date = datetime.date(*name_date)
            offset = (name_date - last_date).days

        change = False
        if fields != prev_fields:
            outfile.write(f'{name}:  Fields:             {", ".join(fields)}\n')
            change = True
        if fields == prev_fields and head != prev_head:
            outfile.write(f'{name}:  Old headers:        {head}\n')
            outfile.write(f'{name}:  New headers:        {head}\n')
            change = True
        if start != prev_start:
            outfile.write(f'{name}:  Start date:         {start}\n')
            change = True
        if offset != prev_offset:
            outfile.write(f'{name}:  Offset (days):      {offset}\n')
            change = True
        if regions != prev_regions:
            outfile.write(f'{name}:  Regions:            {", ".join(regions)}\n')
            change = True
        if uk_maybe_weighted != prev_uk_maybe_weighted:
            outfile.write(f'{name}:  UK nation-weighted: {uk_maybe_weighted}\n')
            change = True
        if en_maybe_weighted != prev_en_maybe_weighted:
            outfile.write(f'{name}:  EN region-weighted: {en_maybe_weighted}\n')
            change = True
        prev_fields = fields
        prev_head = head
        prev_start = start
        prev_regions = regions
        prev_offset = offset
        prev_en_maybe_weighted = en_maybe_weighted
        prev_uk_maybe_weighted = uk_maybe_weighted
        if change:
            outfile.write('\n')

    outfile.write(f'{name}\n')


outdir = Path('out/changes/')
outdir.mkdir(parents=True, exist_ok=True)

indir = Path('download-sample/incidence table/')
with open(outdir / 'incidence table.txt', 'w') as outfile:
    changes_table(indir, 'incidence table_', outfile)

indir = Path('download/incidence/')
with open(outdir / 'incidence.txt', 'w') as outfile:
    changes(indir, 'incidence_', outfile)

indir = Path('download/prevalence_history/')
with open(outdir / 'prevalence_history.txt', 'w') as outfile:
    changes(indir, 'prevalence_history_', outfile)

indir = Path('download/incidence_history/')
with open(outdir / 'incidence_history.txt', 'w') as outfile:
    changes(indir, 'incidence_history_', outfile)
