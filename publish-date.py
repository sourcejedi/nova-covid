#!/usr/bin/env python3
from pathlib import Path
import mmap

def publish_date(indir, prefix,
                 out_en5, out_uk5,
                 out_en6, out_uk6):

    paths = list(indir.glob(prefix + '*.csv'))
    paths.sort()

    out_en = out_en5
    out_uk = out_uk5

    for path in paths:
        # Use all files after method change v5
        if path.name < 'incidence_20211003.csv':
            continue
        # Header line
        if path.name == 'incidence_20211003.csv':
            with path.open('rb') as infile:
                header = next(infile)
                out_en.write(header)
                out_uk.write(header)
        if path.name == 'incidence_20230201.csv':
            out_en = out_en6
            out_uk = out_uk6
            with path.open('rb') as infile:
                header = next(infile)
                out_en.write(header)
                out_uk.write(header)

        with path.open('rb') as infile:
            # You *could* do this efficiently
            # without mmap, but why bother?
            def reversed_lines():
                data = mmap.mmap(infile.fileno(), 0, prot=mmap.PROT_READ)
                j = len(data)
                i = data.rfind(b'\n', 0, j)
                yield data[i+1:j]
                while i >= 0:
                    j = i
                    i = data.rfind(b'\n', 0, j)
                    yield data[i+1:j+1]

            lines = reversed_lines()
            line = next(lines)
            while b',England,' not in line:
                line = next(lines)
            out_en.write(line)
            
            lines = reversed_lines()
            line = next(lines)
            while b',UK,' not in line:
                line = next(lines)
            out_uk.write(line)

indir = Path('download/incidence/')
with (open('out/publish-date.incidence.England.v5.csv', 'wb') as out_en5,
      open('out/publish-date.incidence.England.v6.csv', 'wb') as out_en6,
      open('out/publish-date.incidence.UK.v5.csv', 'wb') as out_uk5,
      open('out/publish-date.incidence.UK.v6.csv', 'wb') as out_uk6):
    publish_date(indir, 'incidence_',
                 out_en5, out_uk5,
                 out_en6, out_uk6)
