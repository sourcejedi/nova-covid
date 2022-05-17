# Build instructions

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
