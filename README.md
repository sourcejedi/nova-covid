ZOE has run for two years, and counting.  I built up a number of scripts to keep an eye on them.  This was my new version ("nova"), to make some cleaner and more sharable scripts.

(I still use the old stuff.  And I still use spreadsheets for convenient graphs etc.  But the cleanup definitely helped).

 * [ZOE Covid Study - the public data files][blog-1]
 * [ZOE Covid Study - part 2 - the method][blog-2]
 * [ZOE Covid Study - confidence intervals][blog-3]
 * [Failure to reproduce calculation of prevalence from incidence used in a scientific paper by ZOE Covid Study][PubPeer]

[blog-1]: https://sourcejedi.github.io/2022/01/31/zoe-covid-study.html
[blog-2]: https://sourcejedi.github.io/2022/02/02/zoe-covid-study-part-2-methods.html
[blog-3]: https://sourcejedi.github.io/2022/02/27/zoe-covid-confidence-intervals.html
[PubPeer]: https://pubpeer.com/publications/3C823DD588CE2A33BE78AD80E9CCDD

Software requirements:
 * Linux/Unix
 * python3
 * gsutil. See first blog post above.
 * LibreOffice Calc, or compatible spreadsheet software.


## Index

`fetch.sh`. Download some ZOE data files (~1GB).

`changes.sh`. Find when ZOE data files changed format etc.

`wilson.py` + `wilson.ods`. Calculate the Wilson score, to reproduce confidence intervals used in method v1, v2, and v3 (!).

`jump.py` + `jump.ods`. Look for "jumps", that can suggest a change in the method.

`prevalence.England.py` + `prevalence.UK.py`. Add up the prevalences for the England / UK regions.

`prevalence_from_incidence/`.  Reproduce the method ZOE use to estimate prevalence from their incidence figures.  See `README.md` in this directory.


## download-sample/

DISCLAIMER: I do not own this data.  I cannot vouch for it.  Do not cite these copies in your academic paper!  I am reposting it to help learn about ZOE methods.


### download-sample/incidence table/

Saved copies of https://covid-assets.joinzoe.com/latest/incidence%20table.csv
