#!/usr/bin/env python3

import os
from pathlib import Path
import csv
import datetime

# https://www.mikulskibartosz.name/wilson-score-in-python-example/
from math import sqrt
def wilson(p, n, z = 1.96):
    denominator = 1 + z**2/n
    centre_adjusted_probability = p + z*z / (2*n)
    adjusted_standard_deviation = sqrt((p*(1 - p) + z*z / (4*n)) / n)

    lower_bound = (centre_adjusted_probability - z*adjusted_standard_deviation) / denominator
    upper_bound = (centre_adjusted_probability + z*adjusted_standard_deviation) / denominator
    return (lower_bound, upper_bound)

def changes_map(indir, prefix, outfile):
    paths = list(indir.glob(prefix + '*.csv'))
    paths.sort()
    prefix_len = len(prefix)

    prev_head = None
    prev_fields = None
    prev_region_count = None
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

            assert f.readline().rstrip() == head
            heads = head.split(',')
            f.seek(0)

            region_count = 0
            read = csv.DictReader(f)
            for row in read:
                region_count += 1
            f.seek(0)

        change = False
        if fields != prev_fields:
            display_fields = [field.replace('\n', ' ') for field in fields]
            outfile.write(f'{name}:  Fields:              {", ".join(display_fields)}\n')
            change = True
        if fields == prev_fields and head != prev_head:
            outfile.write(f'{name}:  Old headers:         {head}\n')
            outfile.write(f'{name}:  New headers:         {head}\n')
            change = True
        if region_count != prev_region_count:
            outfile.write(f'{name}:  # regions:           {region_count}\n')
            change = True
        prev_fields = fields
        prev_head = head
        prev_region_count = region_count
        if change:
            outfile.write('\n')

    outfile.write(f'{name}\n')

def changes_table(indir, prefix, outfile):
    paths = list(indir.glob(prefix + '*.csv'))
    paths.sort()
    prefix_len = len(prefix)

    prev_head = None
    prev_fields = None
    prev_regions = None
    prev_UK_pop = None
    prev_wilson_ci_p = None
    prev_wilson_ci_cases = None
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

            assert f.readline().rstrip() == head
            heads = head.split(',')
            f.seek(0)

            def get_region(row):
                return row.get('region') or row.get('nhser19nm')

            regions = []
            UK_pop = 0
            EN_pop = 0
            EN_pop_file = 0
            read = csv.DictReader(f)
            for row in read:
                region = get_region(row)
                assert region
                assert region not in regions
                regions.append(region)

                pop = float(row['population'])
                assert pop == int(pop)
                pop = int(pop)
                if region == 'England':
                    EN_pop_file = pop
                    UK_pop += EN_pop_file
                elif region in ['Scotland', 'Wales', 'Northern Ireland']:
                    UK_pop += pop
                else:
                    EN_pop += pop
            regions.sort()
            regions_set = set(regions)
            f.seek(0)

            assert(EN_pop == EN_pop_file)
            if UK_pop < 1000*1000:
                UK_pop = ('Less than 1,000,000. ' +
                    'This file has several column headers in the wrong place.')

            # hack. this thing is about methods v1 to v3
            # and v4 doesn't have % +ve, so would need some adaptation.
            if name < '20210721':
                wilson_ci_p = True
                wilson_ci_cases = True

                read = csv.DictReader(f)
                for row in read:
                    region = get_region(row)
                    tests = row.get('# total tests')
                    if tests == 'N/A':
                        continue
                    tests = int(tests)
                    positives = int(row.get('# +ve tests'))
                    p = positives/tests
                    (p_lo,p_up) = wilson(p, tests)

                    # ???
                    if not (region == 'Northern Ireland' and
                            tests == 44 and
                            positives == 2):
                        file_p = row.get('% +ve tests')
                        file_p = float(file_p.strip('%'))/100
                        file_p_lo = row.get('% +ve tests\n95% lower lim.')
                        file_p_lo = float(file_p_lo.strip('%'))/100
                        file_p_up = row.get('% +ve tests\n95% upper lim.')
                        file_p_up = float(file_p_up.strip('%'))/100

                        if not (abs(file_p - p) < 0.000051 and
                                abs(file_p_lo - p_lo) < 0.000051 and
                                abs(file_p_up - p_up) < 0.000051):
                            wilson_ci_p = False
                            #print(f'{name}, {region}, {tests}, {positives}')
                            #print(f'{file_p}, {p}')
                            #print(f'{file_p_lo}, {p_lo}')
                            #print(f'{file_p_up}, {p_up}')
                            #print()

                    file_cases = int(row.get('est. daily\ncases'))
                    file_cases_lo = int(row.get('est. daily\ncases\n95% lower lim.'))
                    file_cases_up = int(row.get('est. daily\ncases\n95% upper lim.'))

                    if p != 0:
                        # brute force un-rounding of cases.
                        # alternative: incidence_history
                        i = -0.51
                        while i < 0.511:
                            cases = file_cases + i
                            cases_lo = cases * (p_lo/p)
                            cases_up = cases * (p_up/p)
                            if (
                                (abs(file_cases_lo - cases_lo) < 0.51 and
                                abs(file_cases_up - cases_up) < 0.51)):
                                    break
                            i += 0.01
                        else:
                            wilson_ci_cases = False
                            #cases = file_cases
                            #cases_lo = cases * (p_lo/p)
                            #cases_up = cases * (p_up/p)

                            #print(f'{name}, {region}, {tests}, {positives}')
                            #print(f'{file_cases}, {file_cases_lo}, {file_cases_up}')
                            #print(f'{cases}, {cases_lo}, {cases_up}')
                            #print()
            else:
                wilson_ci_p = "N/A"
                wilson_ci_cases = "Unknown"
        change = False
        if fields != prev_fields:
            display_fields = [field.replace('\n', ' ') for field in fields]
            outfile.write(f'{name}:  Fields:              {", ".join(display_fields)}\n')
            change = True
        if fields == prev_fields and head != prev_head:
            outfile.write(f'{name}:  Old headers:         {head}\n')
            outfile.write(f'{name}:  New headers:         {head}\n')
            change = True
        if regions != prev_regions:
            outfile.write(f'{name}:  Regions:             {", ".join(regions)}\n')
            change = True
        if UK_pop != prev_UK_pop:
            outfile.write(f'{name}:  UK population:       {UK_pop}\n')
            change = True
        if wilson_ci_p != prev_wilson_ci_p:
            outfile.write(f'{name}:  % +ve Wilson limits: {wilson_ci_p}\n')
            change = True
        if wilson_ci_cases != prev_wilson_ci_cases:
            outfile.write(f'{name}:   case Wilson limits: {wilson_ci_cases}\n')
            change = True
        prev_fields = fields
        prev_head = head
        prev_regions = regions
        prev_UK_pop = UK_pop
        prev_wilson_ci_p = wilson_ci_p
        prev_wilson_ci_cases = wilson_ci_cases
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
    prev_en_lo_quirk = None
    prev_en_up_quirk = None
    prev_uk_lo_quirk = None
    prev_uk_up_quirk = None
    prev_value_fraction = None
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

            lo_field = 'pop_low'
            if lo_field not in fields:
                lo_field = 'covid_in_pop_lo'
            if lo_field not in fields:
                lo_field = 'covid_in_pop_lolim'
            if lo_field not in fields:
                lo_field = None
            up_field = 'pop_up'
            if up_field not in fields:
                up_field = 'covid_in_pop_up'
            if up_field not in fields:
                up_field = 'covid_in_pop_uplim'
            if up_field not in fields:
                up_field = None

            if 'UK' in regions or 'England' in regions:
                uk_maybe_weighted = True
                en_maybe_weighted = True
                en_lo_quirk = True
                en_up_quirk = True
                uk_lo_quirk = True
                uk_up_quirk = True

                uk_mid = 0
                en_mid = 0
                file_uk_mid = 0
                file_en_mid = 0

                file_en_lo = 0
                file_en_up = 0
                en_lo = 0
                en_up = 0

                file_uk_lo = 0
                file_uk_up = 0
                uk_lo = 0
                uk_up = 0

                row = next(read, None)
                assert row
                date = row.get('date')
                assert(date)
                while date == start:
                    mid = row.get(mid_field)
                    assert mid
                    mid = float(mid)

                    lo = row.get(lo_field, "0")
                    lo = float(lo)
                    up = row.get(up_field, "0")
                    up = float(up)

                    region = row.get('region')
                    assert region
                    if region == 'UK':
                        file_uk_mid = mid

                        file_uk_lo = lo
                        file_uk_up = up
                    elif region == 'England':
                        file_en_mid = mid
                        uk_mid += mid

                        file_en_lo = lo
                        file_en_up = up

                        uk_lo += lo
                        uk_up += up
                    else:
                        if region in ['Wales', 'Scotland', 'Northern Ireland']:
                            uk_mid += mid

                            uk_lo += lo
                            uk_up += up
                        else:
                            en_mid += mid

                            en_lo += lo
                            en_up += up

                    row = next(read, None)
                    assert row
                    date = row.get('date')

                if abs(file_en_mid - en_mid) > 0.01:
                    en_maybe_weighted = False
                if abs(file_uk_mid - uk_mid) > 0.01:
                    uk_maybe_weighted = False
                if abs(file_en_lo - en_lo) > 0.01:
                    en_lo_quirk = False
                if abs(file_en_up - en_up) > 0.01:
                    en_up_quirk = False
                if abs(file_uk_lo - uk_lo) > 0.01:
                    uk_lo_quirk = False
                if abs(file_uk_up - uk_up) > 0.01:
                    uk_up_quirk = False

            if 'UK' not in regions:
                uk_maybe_weighted = None
                uk_lo_quirk = None
                uk_up_quirk = None
            if 'England' not in regions:
                en_maybe_weighted = None
                en_lo_quirk = None
                en_up_quirk = None
            if not lo_field:
                en_lo_quirk = None
                uk_lo_quirk = None
            if not up_field:
                en_up_quirk = None
                uk_up_quirk = None
            f.seek(0)

            value_fraction = None
            read = csv.DictReader(f)
            row = next(read, None)
            assert row
            date = row.get('date')
            assert(date)
            while date == start:
                mid = row.get(mid_field)
                assert mid
                mid = float(mid)
                if mid != 0:
                    vf = (mid != int(mid))
                    if value_fraction == None:
                        value_fraction = vf
                    else:
                        if value_fraction != vf:
                            value_fraction = 'mixed ?!'
                row = next(read, None)
                assert row
                date = row.get('date')
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
            name_date = [name[:4], name[4:6], name[6:8]]
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
        if en_lo_quirk != prev_en_lo_quirk:
            outfile.write(f'{name}:  Suspect EN CI (lo): {en_lo_quirk}\n')
            change = True
        if en_up_quirk != prev_en_up_quirk:
            outfile.write(f'{name}:  Suspect EN CI (up): {en_up_quirk}\n')
            change = True
        if uk_lo_quirk != prev_uk_lo_quirk:
            outfile.write(f'{name}:  Suspect UK CI (lo): {uk_lo_quirk}\n')
            change = True
        if uk_up_quirk != prev_uk_up_quirk:
            outfile.write(f'{name}:  Suspect UK CI (up): {uk_up_quirk}\n')
            change = True
        if value_fraction != prev_value_fraction:
            outfile.write(f'{name}:  Fractional value:   {value_fraction}\n')
            change = True
        prev_fields = fields
        prev_head = head
        prev_start = start
        prev_regions = regions
        prev_offset = offset
        prev_en_maybe_weighted = en_maybe_weighted
        prev_uk_maybe_weighted = uk_maybe_weighted
        prev_en_lo_quirk = en_lo_quirk
        prev_en_up_quirk = en_up_quirk
        prev_uk_lo_quirk = uk_lo_quirk
        prev_uk_up_quirk = uk_up_quirk
        prev_value_fraction = value_fraction
        if change:
            outfile.write('\n')

    outfile.write(f'{name}\n')

outdir = Path('out/changes/')
outdir.mkdir(parents=True, exist_ok=True)

indir = Path('download/utla_prevalence_map/')
with open(outdir / 'utla_prevalence_map.txt', 'w') as outfile:
    changes_map(indir, 'utla_prevalence_map_', outfile)

indir = Path('download/lad_prevalence_map/')
with open(outdir / 'lad_prevalence_map.txt', 'w') as outfile:
    changes_map(indir, 'lad_prevalence_map_', outfile)

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
