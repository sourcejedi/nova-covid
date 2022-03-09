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

            assert f.readline().rstrip() == head
            heads = head.split(',')
            date_field = 0
            if not heads[0]:
                date_field = 1
            region_field = date_field + 1
            assert heads[date_field] == 'date'
            assert heads[region_field] == 'region'

            try:
                mid_field = heads.index('pop_mid')
            except ValueError:
                try:
                    mid_field = heads.index('covid_in_pop')
                except ValueError:
                    mid_field = heads.index('active_cases')

            # Optimized inner loop ahead
            skip_slow = False
            if not skip_slow:
                uk_maybe_weighted = True
                en_maybe_weighted = True
                if 'UK' not in regions and 'England' not in regions:
                    mid_field = None

                prev_date = None
                regions2_set = regions_set
                uk_mid = 0
                en_mid = 0
                file_uk_mid = 0
                file_en_mid = 0
                while True:
                    line = f.readline()
                    if not line:
                        assert regions2_set == regions_set
                        break
                    line = line.split(',')
                    date = line[date_field]
                    region2 = line[region_field]
                    if date != prev_date:
                        assert regions2_set == regions_set
                        regions2_set = set()

                        if mid_field:
                            if abs(file_en_mid - en_mid) > 0.01:
                                en_maybe_weighted = False
                            if abs(file_uk_mid - uk_mid) > 0.01:
                                uk_maybe_weighted = False
                            uk_mid = 0
                            en_mid = 0
                        prev_date = date
                    regions2_set.add(region2)

                    # lazy coding: this won't be tested for the last date.
                    # testing this separately from 'incidence table' was
                    # probably overkill.  Oh well.
                    if mid_field:
                        mid = float(line[mid_field])
                        if region2 == 'UK':
                            file_uk_mid = mid
                        elif region2 == 'England':
                            file_en_mid = mid
                        else:
                            uk_mid += mid
                            if region2 not in ['Wales', 'Scotland', 'Northern Ireland']:
                                en_mid += mid

                if 'UK' not in regions:
                    uk_maybe_weighted = None
                if 'England' not in regions:
                    en_maybe_weighted = None
            else: # skip_slow
                uk_maybe_weighted = None
                en_maybe_weighted = None

                for line in f:
                    pass
                (date, region2, _) = line.split(',', 2+shift)[shift:]

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
            outfile.write(f'{name}:  UK region-weighted: {uk_maybe_weighted}\n')
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
