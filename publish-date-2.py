#!/usr/bin/env python3
from pathlib import Path
import mmap

class PublishDate:
    __slots__ = ('out_uk', 'out_en')
    def __init__(self):
        self.out_uk = [
            open('out/publish-date.incidence.UK.v5.csv', 'wb'),
            open('out/publish-date-1.incidence.UK.v5.csv', 'wb'),
            open('out/publish-date-2.incidence.UK.v5.csv', 'wb')
        ]
        self.out_en = [
            open('out/publish-date.incidence.England.v5.csv', 'wb'),
            open('out/publish-date-1.incidence.England.v5.csv', 'wb'),
            open('out/publish-date-2.incidence.England.v5.csv', 'wb')
        ]
        
    def __enter__(self):
        return self
    def __exit__(self, *_):
        for f in self.out_uk:
            f.close()
        for f in self.out_en:
            f.close()

    def run(self):
        indir = Path('download/incidence/')
        prefix = 'incidence_'
        
        paths = list(indir.glob(prefix + '*.csv'))
        paths.sort()

        for path in paths:
            # Use all files after method change v5
            if path.name < 'incidence_20211003.csv':
                continue
            # Header line
            if path.name == 'incidence_20211003.csv':
                with path.open('rb') as infile:
                    header = next(infile)
                    for out_en in self.out_en:
                        out_en.write(header)
                    for out_uk in self.out_uk:
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
                for out_en in self.out_en:
                    line = next(lines)
                    while b',England,' not in line:
                        line = next(lines)
                    out_en.write(line)
                
                lines = reversed_lines()
                for out_uk in self.out_uk:
                    line = next(lines)
                    while b',UK,' not in line:
                        line = next(lines)
                    out_uk.write(line)

with PublishDate() as publish_date:
    publish_date.run()
