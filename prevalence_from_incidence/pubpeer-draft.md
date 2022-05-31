*Draft comment on [Detecting COVID-19 infection hotspots in England using large-scale self-reported data from a mobile application: a prospective, observational study][hotspot-paper], intended for pubpeer.com.*

[hotspot-paper]: https://www.thelancet.com/journals/lanpub/article/PIIS2468-2667(20)30269-3/fulltext

---

I thank the study for sharing files of incidence data.  I tried to use a method from this paper, which estimates prevalence based on  incidence.  Unfortunately my result did not match the prevalence published by the study.  The same issue applies to this paper.

# Contents

1. Inconsistency between Figure&nbsp;1 and Figure&nbsp;2
2. Potential alternative version of Figure 2
3. Details and errata

# 1. Inconsistency between Figure&nbsp;1 and Figure&nbsp;2

We can show the data in Figure 1 and Figure 2 are not consistent with each other.  It may be the paper has the wrong version of Figure 2.

Figure 1 shows incidence (Figure 1A) and prevalence (Figure 1B), estimated from Symptom Study assessments and swab results.  The prevalence labelled $P_H$ is estimated indirectly, from a combination of Symptom Study incidence $I_t$, and the recovery model $M$ shown in Figure 2.  The appendix expresses this as:

$P_t = I_{t:t+30} \cdot (1-CDF(M))$

The Symptom Study published data files of incidence and prevalence.  By overlaying this data on Figure 1A and 1B, we can see this data matches well.  The prevalence from the data files is very slightly lower. (Graph 1)

We have incidence data.  We have the gamma distribution parameters for the recovery model, which are written in Figure 2.  We can write a program to evaluate the equation above.  My results were about 14% lower than the prevalence in the data file.  By overlaying this on Figure 1B, we can see this much larger difference. (Graph 1B)

I checked my program by running it on `test-in.csv`, which sets incidence to 100 for one day and 0 thereafter.  For each subsequent day, we can subtract $P_t$ from 100 to show the cumulative recovery percentage.  Overlaying this on Figure 2B, the cumulative recovery matches very well.  The inconsistency does not appear to be a mistake in my programming. (Graph 2B)


## Graph 1 - Figure 1 overlay

![](https://github.com/sourcejedi/nova-covid/blob/main/prevalence_from_incidence/figure-1.png?raw=true)

## Graph 2 - Figure 2 overlay

![](https://github.com/sourcejedi/nova-covid/blob/main/prevalence_from_incidence/figure-2.png?raw=true)


# 2. Potential alternative version of Figure 2

Similar to my `test-in.csv`, there is a period in later Symptom Study files where incidence for Northern Ireland falls to 0, and stays at 0 for at least 30 days.  So we can use the same technique as with `test-in.csv` to reverse engineer the recovery model, by looking at the prevalence file.  I modified my program to use this recovery model by default.  Using my program on incidence data, it can exactly reproduce the England prevalence file plotted in Graph 1B.

This alternative recovery model is shown in Graph 3B.  It illustrates why the gamma model produced lower results.  The area above the curve, equal to $\sum 1-CDF(M)$, was 14% lower in the gamma model compared to this reverse engineered model.

The values of the recovery function are included in my full release linked below.  These values could reproduce the statement "For example, we observe that only 52.2% of people recover within 13 days"[[Symptom Study website]](https://covid.joinzoe.com/post/data-update-prevalence-covid).  This statement could not be made about Figure 2 from the paper.

The recovery model might include some random variation from the original data (Graph 3A).  However the prevalence calculation uses the cumulative distribution function, which is relatively smooth (Graph 3B).

The seven initial zeroes in Graph 3 might be explained by the appendix: "We defined recovery as either seven days of uninterrupted healthy reporting in the app or..."

## Graph 3 - Alternative data for Figure 2

![](https://github.com/sourcejedi/nova-covid/blob/main/prevalence_from_incidence/figure-2-alt.png?raw=true)


# 3. Details and errata

Link: [[my program and technical methods]][prevalence_from_incidence].

[prevalence_from_incidence]: https://github.com/sourcejedi/nova-covid/tree/main/prevalence_from_incidence


If you check my technical methods linked above, you are likely to notice the following:

1. Figure 2 says the gamma fit uses parameters α=2.595, β=4.48.  I matched the curve in Figure 2 (see Graph 2) using `scipy.stats.gamma(a=2.595, scale=4.48)`.  This might be confusing, because β is usually used to represent "shape", equal to $1 / scale$.

2. "Figure 1 Daily incidence in the UK [...] (A) and daily prevalence in the UK [...] (B)" should say "England", not "UK".  The article text is correct on this point.

3. Figure 1A shows Symptom Study incidence for England.  This figure matches very well with the "England" region in the file `incidence_20210205.csv`.

   However, the data file also has incidences for the 7 NHS regions of England.  For some of the time, the sum of the England sub-regions is slightly higher than the value given for "England".

   (I have seen the incidence this file shows for "England" is estimated by pooling all assessments and swab results from England.  It does not take into account which sub-region they come from.

   This makes it simpler to calculate a confidence interval for the graph, using the method in the appendix.)

4. Figure 1B shows Symptom Study prevalence $P_H$.  This matches well with the sum of the prevalences in the 7 NHS regions, that were published in `prevalence_history_20210209.csv`.  Although, the prevalence file data is very slightly lower.

   Unlike the incidence file, this prevalence file does not contain a series for "England" overall.
   
   I ran my calculation of $P_t$ using the sum of regional incidences, so it was comparable with the prevalence data file.
   
   You could try using the "England" incidence instead, but it does not really change the picture.  The resulting $P_t$ is slightly lower.  If anything, this would increase the inconsistency when comparing to Figure 1B.

5. It does not make a difference whether you estimate prevalence for the 7 NHS regions and then add them up, or add up their incidences first and then convert the total incidence to a prevalence.  If you look at the maths, you are just adding up numbers in a different order.  I found it simpler to add up the incidences first.
