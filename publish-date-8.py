#!/usr/bin/env python3

import os
from pathlib import Path
import itertools
import csv
import mmap

N=9

def pub_history(indir, prefix, out_en, out_uk):
    heads = [b'file'] + [str(i).encode('ascii') for i in range(0, -N, -1)]
    header = b','.join(heads) + b'\n'
    for outfile in out_en, out_uk:
        outfile.write(header)

    paths = list(indir.glob(prefix + '*.csv'))
    paths.sort()
    prefix_len = len(prefix)

    for path in paths:
        name = path.name[prefix_len:-4]
        print(path)
        with path.open() as f:
            head = f.readline()
            assert head
            head = head.rstrip()
            assert head

            heads = head.split(',')
            date_field = 0
            if not heads[0]:
                date_field = 1
            assert heads[date_field] == 'date'
            
            region_field = heads.index('region')

            field_names = ['pop_mid', 'covid_in_pop']
            for field_name in field_names:
                try:
                    mid_field = heads.index(field_name)
                    break
                except ValueError:
                    pass
            else:
                raise Exception(f'{path}: could not find one of {field_names}')

            # You *could* do this efficiently
            # without mmap, but why bother?
            def reversed_lines():
                data = mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)
                j = len(data)
                i = data.rfind(b'\n', 0, j)
                yield data[i+1:j]
                while i >= 0:
                    j = i
                    i = data.rfind(b'\n', 0, j)
                    yield data[i+1:j+1]

            def reversed_values(region):
                lines = reversed_lines()
                while True:
                    line = next(lines)
                    if line is None:
                        return

                    row = line.split(b',')
                    if region not in row:
                        continue

                    yield row[mid_field]

            for (region, outfile) in [(b'England', out_en), (b'UK', out_uk)]:
                values_iter = reversed_values(region)
                values = list(itertools.islice(values_iter, N))
                line = b','.join([name.encode('ascii')] + values)
                outfile.write(line)
                outfile.write(b'\n')

outdir = Path('out/')
outdir.mkdir(parents=True, exist_ok=True)

indir = Path('download/incidence/')
with (open(outdir / 'publish-date-8.incidence.England.csv', 'wb') as out_en,
      open(outdir / 'publish-date-8.incidence.UK.csv', 'wb') as out_uk):
    pub_history(indir, 'incidence_', out_en, out_uk)
