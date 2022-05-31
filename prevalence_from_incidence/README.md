## Index

* `prevalence.py`:  Reproduce how ZOE estimate prevalence from their incidence figures.  See code comments at top of file.

  Alternatively, if run with `--use-gamma`, try to reproduce the method specified in ZOE's "hotspot" paper.  This gives results that are about 14% lower.

* `gamma_paper-vs-extract.ods`:  graph sample outputs from `prevalence.py`.  Also overlay them on Figure 1 from the "hotspot" paper.

* `test-out.ods`:  graph the recovery model used, and overlay it on Figure 2 from the "hotspot" paper.  The recovery model is extracted from `prevalence.py` by running it on an artificial test input, `test-in.csv`.

* `pubpeer-draft.md`:  Draft comment on the "hotspot" paper, intended for pubpeer.com.

See [Detecting COVID-19 infection hotspots in England using large-scale self-reported data from a mobile application: a prospective, observational study][hotspot-paper].

[hotspot-paper]: https://www.thelancet.com/journals/lanpub/article/PIIS2468-2667(20)30269-3/fulltext


## Method to re-make the graphs

At the top level:

1. Download ALL input files from ZOE (about 1 gigabyte):

       ./fetch.sh

   OR use sample input data:

       mkdir -p download
       cp -r download-sample/. download/

2. Process data:

       ./prevalence_from_incidence/build.sh

3. Now open the desired spreadsheet prevalence_from_incidence/*.ods,
   and update the graph data.  In LibreOffice, this is:

    * Edit → Links to external files.
    * Select all, then Update.
