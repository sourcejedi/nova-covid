#!/usr/bin/env python3
import os
from pathlib import Path
import csv

outdir = Path('out/changes/')
outdir.mkdir(parents=True, exist_ok=True)

def changes(indir, prefix, outfile):
    paths = list(indir.glob(prefix + '*.csv'))
    paths.sort()
    prefix_len = len(prefix)
    prev_head = None
    prev_start = None
    for path in paths:
        with path.open() as f:
            head = f.readline()
            head = head.rstrip()
            f.seek(0)
            read = csv.DictReader(f)
            row = next(read)
            assert row
            assert 'date' in row
            start = row['date']
        name = path.name[prefix_len:-4]
        if head != prev_head:
            outfile.write(f'{name}\tField headings: {head}\n')
            prev_head = head
        if start != prev_start:
            outfile.write(f'{name}\t    Start date: {start}\n')
            prev_start = start
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
