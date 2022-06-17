#!/usr/bin/env python3
from pathlib import Path
import mmap

def publish_date(indir, prefix, outfile):
    paths = list(indir.glob(prefix + '*.csv'))
    paths.sort()

    for path in paths:
        # Use all files after method change v5
        if path.name < 'incidence_20211003.csv':
            continue
        # Header line
        if path.name == 'incidence_20211003.csv':
            with path.open('rb') as infile:
                outfile.write(next(infile))

        with path.open('rb') as infile:
            # You *could* do this efficiently
            # without mmap, but why bother?
            data = mmap.mmap(infile.fileno(), 0, prot=mmap.PROT_READ)
            
            j = len(data)
            i = data.rfind(b'\n', 0, j)
            last_en = data[i+1:j+1]
            while not b',England,' in last_en:
                j = i
                i = data.rfind(b'\n', 0, j)
                last_en = data[i+1:j+1]

            outfile.write(last_en)

indir = Path('download/incidence/')
with open('out/publish-date.incidence.England.v5.csv', 'wb') as outfile:
    publish_date(indir, 'incidence_', outfile)
