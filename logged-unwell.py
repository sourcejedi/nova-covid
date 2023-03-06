#!/usr/bin/env python3
from pathlib import Path
import csv
from collections import namedtuple

OutputRow = namedtuple('OutputRow',
                       ['region', 'well', 'unwell', 'logged', 'percent_unwell'])

def one_sick(path, writer):
    name = path.name[:-4]
    date = '-'.join([name[:-4], name[-4:-2], name[-2:]])

    with path.open() as infile:   
        rows = {}
        for line in infile:
            line = line.rstrip()
            line = line.rsplit(sep=' ', maxsplit=4)
            (region, well, unwell, percent_round, sigil) = line
            if region == 'TOTAL':
                region = 'UK'
            well = int(well)
            unwell = int(unwell)
            percent_round = float(percent_round)
            assert sigil == '%'
            del sigil
            logged = well + unwell
            percent = unwell / logged * 100
            assert round(percent * 100) == round(percent_round * 100)
            del percent_round
            rows[region] = OutputRow(region, well, unwell, logged, percent)
        UK = rows.pop('UK')
        nations = []
        for name in ['Wales', 'Scotland', 'Northern Ireland']:
            nations.append(rows.pop(name))
        # rows is now only the regions of England
        well = 0
        unwell = 0
        for row in rows.values():
            well += row.well
            unwell += row.unwell
        logged = well + unwell
        england = OutputRow('England', well, unwell, logged,
                            unwell / logged * 100)
        nations.insert(0, england)
        del england
        well = 0
        unwell = 0
        for nation in nations:
            well += nation.well
            unwell += nation.unwell
        assert UK.well == well
        assert UK.unwell == unwell
        rows = [rows[region] for region in sorted(rows.keys())]
        rows += nations
        del nations
        rows.append(UK)
        del UK
        for row in rows:
            writer.writerow((date,) + row)

def all_sick(indir, outfile):
    writer = csv.writer(outfile)
    writer.writerow(['date',
                     'region',
                     '# users who logged feeling well',
                     '# users who logged feeling unwell',
                     '# users who logged',
                     '% users who logged feeling unwell'])

    paths = list(indir.glob('*.txt'))
    paths.sort()
    for path in paths:        
        try:
            one_sick(path, writer)
        except Exception as e:
            print (f"Error processing '{path.name}'")
            raise

indir = Path('logged-unwell.txt')
with open('out/logged-unwell.csv', 'w') as outfile:
    all_sick(indir, outfile)


import os
import sys
def shell(script):
    rc = os.system(script)
    if rc != 0:
        print(script)
        sys.exit(1)

shell('head -n1 out/logged-unwell.csv > out/logged-unwell.England.csv')
shell('grep ,England, out/logged-unwell.csv >> out/logged-unwell.England.csv')

shell('head -n1 out/logged-unwell.csv > out/logged-unwell.Scotland.csv')
shell('grep ,Scotland, out/logged-unwell.csv >> out/logged-unwell.Scotland.csv')
