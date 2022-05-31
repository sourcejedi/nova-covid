ZOE still seems to be a thing.  So I have cleaned up some of my
scripts, and I am posting them on GitHub.

 * [ZOE Covid Study - the public data files][blog-1]
 * [ZOE Covid Study - part 2 - the method][blog-2]
 * [ZOE Covid Study - confidence intervals][blog-3]
 * [Failure to reproduce calculation of prevalence from incidence used in a scientific paper by ZOE Covid Study][pubpeer-draft]

[blog-1]: https://sourcejedi.github.io/2022/01/31/zoe-covid-study.html
[blog-2]: https://sourcejedi.github.io/2022/02/02/zoe-covid-study-part-2-methods.html
[blog-3]: https://sourcejedi.github.io/2022/02/27/zoe-covid-confidence-intervals.html
[pubpeer-draft]: https://github.com/sourcejedi/nova-covid/blob/main/prevalence_from_incidence/pubpeer-draft.md

Software requirements:
 * Linux/Unix
 * gsutil - see first blog post above
 * python3
 * scipy module for python3
 * LibreOffice or compatible ODS reader


## Index

`fetch.sh`. Download some ZOE data files (~1GB).

`changes.sh`. Find when ZOE data files changed format etc.

`wilson.py` + `wilson.ods`. Calculate the Wilson score, to reproduce confidence intervals used in method v1, v2, and v3 (!).

`jump.py` + `jump.ods`. Look for "jumps", that can suggest a change in the method.

`prevalence.England.py` + `prevalence.UK.py`. Add up the prevalences for the England / UK regions.

`prevalence_from_incidence/`.  Reproduce how ZOE estimate prevalence from their incidence figures.  See `README.md` in this directory.


## download-sample/

DISCLAIMER: I do not own this data.  I cannot vouch for it.  Do not cite these copies in your academic paper!  I am reposting it to help learn about ZOE methods.


### download-sample/incidence table/

Saved copies of https://covid-assets.joinzoe.com/latest/incidence%20table.csv
