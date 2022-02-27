#!/usr/bin/env python3
import os
from pathlib import Path

outdir = Path('out/changes/')
outdir.mkdir(parents=True, exist_ok=True)

def changes(indir, prefix, outfile):
    paths = list(indir.glob(prefix + '*.csv'))
    paths.sort()
    prefix_len = len(prefix)
    prev_head = None
    for path in paths:
        with path.open() as f:
            head = f.readline()
        head = head.rstrip()
        if head != prev_head:
            outfile.write(f'{path.name[prefix_len:-4]}  {head}\n')
            prev_head = head

indir = Path('download-zoe/incidence/')
with open(outdir / 'changes_incidence', 'w') as outfile:
    changes(indir, 'incidence_', outfile)

indir = Path('download-zoe/prevalence_history/')
with open(outdir / 'changes_prevalence_history', 'w') as outfile:
    changes(indir, 'prevalence_history_', outfile)

indir = Path('download-zoe/incidence_history/')
with open(outdir / 'changes_incidence_history', 'w') as outfile:
    changes(indir, 'incidence_history_', outfile)
