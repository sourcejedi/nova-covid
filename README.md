ZOE have run a COVID study for two years and counting.  I wrote some scripts to keep an eye on them.  This is my new version ("nova") with cleaner, more sharable scripts.

(Admittedly, I still use other scripts.  And I still use spreadsheets for convenient graphs etc).

See also:

 * [ZOE Covid Study - the public data files][blog-1]
 * [ZOE Covid Study - part 2 - the method][blog-2]
 * [ZOE Covid Study - confidence intervals][blog-3]
 * [Failure to reproduce the calculation of prevalence from incidence in a scientific paper by ZOE Covid Study][PubPeer]
   * [Source code][prevalence_from_incidence]

[blog-1]: https://sourcejedi.github.io/2022/01/31/zoe-covid-study.html
[blog-2]: https://sourcejedi.github.io/2022/02/02/zoe-covid-study-part-2-methods.html
[blog-3]: https://sourcejedi.github.io/2022/02/27/zoe-covid-confidence-intervals.html
[PubPeer]: https://pubpeer.com/publications/3C823DD588CE2A33BE78AD80E9CCDD
[prevalence_from_incidence]: https://github.com/sourcejedi/nova-covid/prevalence_from_incidence/

Software requirements:

 * Linux/Unix
 * python3
 * gsutil. See first blog post above.
 * LibreOffice Calc, or compatible spreadsheet software.


## Index

`fetch.sh`. Download some ZOE data files (~1GB).

`publish-date.py` + `publish-date.incidence.England.v5.ods`. Graph the ZOE data (England) by publish date.

`changes.sh`. Find when ZOE data files changed format etc.

`jump.py` + `jump.ods`. Look for "jumps", that can suggest a change in the method.

`prevalence.England.py` + `prevalence.UK.py`. Add up the prevalences for the England / UK regions.

`prevalence_from_incidence/README.md`. Failure to reproduce the calculation of prevalence from incidence in a scientific paper by ZOE Covid Study.

`prevalence_from_incidence.py`. Reproduce the method ZOE use to estimate prevalence from their incidence figures.

`check_p_from_i.py`. Check prevalence calculation against the ZOE files, where possible.

`logged-unwell.*`. Graph some raw daily totals, manually copied from from the daily reports.

`newly_sick_table.*`. "Daily percentage of contributors who report new symptoms, with or without a positive COVID test result", per region.  The data files for this are not in the covid-public-data bucket. `fetch.sh` downloads them from the app backend.  I only write this sort of thing [when I have a reason to](https://twitter.com/sourcejedi/status/1557730035338842112).

`wilson.py` + `wilson.ods`. Calculate the Wilson score, to reproduce confidence intervals used in method v1, v2, and v3 (!).


## download-sample/

DISCLAIMER: I do not own this data.  I cannot vouch for it.  Do not cite these copies in your academic paper!  I am reposting it to help learn about ZOE methods.


### download-sample/incidence table/

Saved copies of https://covid-assets.joinzoe.com/latest/incidence%20table.csv
