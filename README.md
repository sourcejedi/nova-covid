ZOE still seems to be a thing.  So I'm cleaning up / revising
a few of my scripts for GitHub.

 * https://sourcejedi.github.io/2022/01/31/zoe-covid-study.html 
 * https://sourcejedi.github.io/2022/02/02/zoe-covid-study-part-2-methods.html

Requirements:
 * Linux/Unix
 * gsutil (see first blog)
 * python3
 * LibreOffice, or other ODS reader

## Index

`fetch.sh`. Download some ZOE data files (~1GB).

`changes.sh`. Find when ZOE data files changed format etc.

`tail.sh` + `jump.ods`. Crude, manual spreadsheet to find "jumps", indicating a new method.

`prevalence.England.py` + `prevalence.UK.py`. Add up the prevalences for the England / UK regions.

## download-sample/

DISCLAIMER: I do not own this data.  I cannot vouch for it.  Do not cite these copies in your academic paper!  I am reposting it to help find out about ZOE methods.

### download-sample/incidence table/

Saved copies of https://covid-assets.joinzoe.com/latest/incidence%20table.csv
