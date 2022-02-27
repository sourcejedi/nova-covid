#!/usr/bin/env python3
import os
from pathlib import Path
import csv
import datetime

outdir = Path('out/changes/')
outdir.mkdir(parents=True, exist_ok=True)

def changes(indir, prefix, outfile):
    paths = list(indir.glob(prefix + '*.csv'))
    paths.sort()
    prefix_len = len(prefix)

    prev_head = None
    prev_fields = None
    prev_start = None
    prev_regions = None
    prev_offset = None
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

            # Optimized inner loop ahead
            slow_check = True
            if slow_check:
                assert f.readline().rstrip() == head
                heads = head.split(',')

                shift = 0
                if not heads[0]:
                    shift = 1
                heads = heads[shift:]
                assert heads[0] == 'date'
                assert heads[1] == 'region'

                prev_date = None
                regions2_set = regions_set
                while True:
                    line = f.readline()
                    if not line:
                        assert regions2_set == regions_set
                        break
                    (date, region2, _) = line.split(',', 2+shift)[shift:]
                    if date != prev_date:
                        assert regions2_set == regions_set
                        regions2_set = set()
                        prev_date = date
                    regions2_set.add(region2)
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
            outfile.write(f'{name}:  Fields:        {", ".join(fields)}\n')
            change = True
        if fields == prev_fields and head != prev_head:
            outfile.write(f'{name}:  Old headers:   {head}\n')
            outfile.write(f'{name}:  New headers:   {head}\n')
            change = True
        if start != prev_start:
            outfile.write(f'{name}:  Start date:    {start}\n')
            change = True
        if offset != prev_offset:
            outfile.write(f'{name}:  Offset (days): {offset}\n')
            change = True
        if regions != prev_regions:
            outfile.write(f'{name}:  Regions:       {", ".join(regions)}\n')
            change = True
        prev_fields = fields
        prev_head = head
        prev_start = start
        prev_regions = regions
        prev_offset = offset
        if change:
            outfile.write('\n')

    outfile.write(f'{name}\n')

indir = Path('download-zoe/incidence/')
with open(outdir / 'changes_incidence', 'w') as outfile:
    changes(indir, 'incidence_', outfile)

indir = Path('download-zoe/prevalence_history/')
with open(outdir / 'changes_prevalence_history', 'w') as outfile:
    changes(indir, 'prevalence_history_', outfile)

indir = Path('download-zoe/incidence_history/')
with open(outdir / 'changes_incidence_history', 'w') as outfile:
    changes(indir, 'incidence_history_', outfile)
