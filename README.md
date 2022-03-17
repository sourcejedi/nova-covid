ZOE still seems to be a thing.  So I'm cleaning up / revising
a few of my scripts for GitHub.

 * [ZOE Covid Study - the public data files](https://sourcejedi.github.io/2022/01/31/zoe-covid-study.html)
 * [ZOE Covid Study - part 2 - the method](https://sourcejedi.github.io/2022/02/02/zoe-covid-study-part-2-methods.html)
 * [ZOE Covid Study - confidence intervals](https://sourcejedi.github.io/2022/02/27/zoe-covid-confidence-intervals.html)

Requirements:
 * Linux/Unix
 * gsutil (see first blog)
 * python3
 * LibreOffice, or other ODS reader

## Index

`fetch.sh`. Download some ZOE data files (~1GB).

`changes.sh`. Find when ZOE data files changed format etc.

`wilson.py` + `wilson.ods`. Calculate the Wilson score, to reproduce confidence intervals used in method v1, v2, and v3 (!).

`tail.sh` + `tail-jump.ods`. Simple manual spreadsheet to find "jumps", suggesting a new method.

`prevalence.England.py` + `prevalence.UK.py`. Add up the prevalences for the England / UK regions.

## download-sample/

DISCLAIMER: I do not own this data.  I cannot vouch for it.  Do not cite these copies in your academic paper!  I am reposting it to help find out about ZOE methods.

### download-sample/incidence table/

Saved copies of https://covid-assets.joinzoe.com/latest/incidence%20table.csv
