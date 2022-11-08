#!/usr/bin/env python3
#
# If you use pypy3, this program can run up to 2x faster. Heh.
#
# This program relies on dictionaries preserving insertion order,
# which is guaranteed since python 3.7.
#
# We also assume input lines are in a convenient order,
# where the date value never decreases.

import csv
import os
import os.path
import sys
from collections import namedtuple

if sys.version_info < (3, 7):
    sys.exit('This script is designed to run on python 3.7 or higher')


KEY_FIELDS = [
    'date',         # publish date - 1.
    'region',       # large region, originally based on the England NHS regions.
    'UTLA19CD',     # upper tier local authority
    'lad16cd',      # local authority district
    'age_group',    # age group
    'imd']          # index of material deprivation (1 to 3)
Keys = namedtuple('Keys', KEY_FIELDS)
Record = namedtuple('Record', ('keys', 'values'))


def parse_values(row):
    values = {}

    def read_float(field):
        assert field in row
        assert row[field] != ''
        value = float(row[field])
        assert value >= 0.0
        values[field] = value

    def read_int(field):
        assert field in row
        assert row[field] != ''
        value = float(row[field])
        value_int = int(value)
        assert value_int == value
        assert value_int >= 0
        values[field] = value_int

    # We deal with this field later.  Don't worry about it in this function.
    # Spoiler: it is nothing to do with gender.
    read_int('gender')

    # The number of users who responded in the last 7 days.
    # This number of days is consistent with:
    #  1. The 2020 paper titled "Detecting COVID-19 infection hotspots..."
    #  2. Where the current daily PDF report says "based on the most recent
    #     report for each contributor that logged during the previous 7 days".
    #  3. Comparing the unhealthy/respondent fraction to the daily numbers in
    #     newly_sick_table*.csv, around the sharp edges from the anomaly here:
    #     https://sourcejedi.github.io/2022/08/24/zoe-covid-3-day-bug.html
    read_int('respondent_count')

    # The number of users in the last 7 days, who logged feeling "unwell"
    # in their most recent response.
    read_int('unhealthy_count')

    # Used in u_fraction (below).  Does not directly correspond to
    # official explanations.
    read_int('unhealthy_unk_count')

    # The number of unwell responders who are predicted to have covid,
    # based on a symptom model.
    read_int('predicted_covid_positive_count')

    # *_prob fields feel like red herrings.  We can see some relationships,
    # but I can't connect them to anything outside this file.
    read_float('predicted_covid_positive_prob')

    # Overall population for this strata, from census or whatever.
    # These are treated as fixed, across the whole time series.
    read_int('population')

    # (In theory you could have issues e.g. if the population increased.
    #  I guess you would discard supernumerary respondents, selected randomly.)
    assert values['respondent_count'] <= values['population']

    assert values['unhealthy_count'] <= values['respondent_count']
    assert values['unhealthy_unk_count'] <= values['unhealthy_count']

    # I can think of one hypothesis for unhealthy_unk_count.  In June 2022,
    # ZOE transitioned to a new reporting method.  This requires setting up a
    # "usual self" (and AFAICT, a new research consent).  If (like me) you
    # haven't set up the new method, you can still make reports using the old
    # method.
    # Link: https://health-study.joinzoe.com/post/new-daily-report-usual-self
    #
    # Initially, new-style reports were not used in published estimates.
    # At the same time we saw a temporary sharp drop in the number of reports
    # used in the incidence data files ("active_users" column).
    #
    # From the daily PDF report:
    # 2022-06-10: The new symptom reporting flow is available to 80% of App users who
    # consented to the ZOE Health Study. While we transition to this new flow, COVID
    # figures will be computed on the remaining 20% of users. As a result, during the
    # transition period, there may be greater uncertainty around our COVID figures due to
    # the smaller sample size. We will provide a further update once we have fully
    # migrated the COVID figures to the new symptom reporting flow..
    #
    # 2022-06-22: From 22nd June, the new symptom reporting flow is available to 100%
    # of App users who consented to the ZOE Health Study. We have fully migrated the
    # COVID figures to the new symptom reporting flow and from this day, we compute
    # our estimates on 100% of the eligible user base, except for local prevalence figures
    # which are smoothed over two weeks and they will be gradually including more
    # users.
    #
    # Looking at all the equations with u_fraction below, you might guess
    # unhealthy_count includes all "unhealthy" reports, and
    # unhealthy_unk_count includes only new-style reports.
    #
    # However, that wouldn't explain why u_fraction would be low e.g. 20%
    # overall, 12% in the 35-54 age group.  And why it *fell* during the first
    # week, or why it stays nearly 100% for 0-17.  According to the blog, 0-17
    # can only be reported by an adult on their behalf, and this process does
    # not use the new method...
    #
    # Revised hypothesis: unhealthy_unk_count includes only *old* style reports.
    # This sounds undesirable for the official UTLA estimates.
    #
    # This still doesn't explain why we appear to use
    # (respondent_count * u_fraction) as a denominator.  I.e. why wouldn't the
    # denominator just be the total number of reports from users who didn't
    # opt in to the new method?  It's as if that number is somehow not
    # available, and we're using a crude approximation instead.

    if values['unhealthy_count']:
        u_fraction = values['unhealthy_unk_count'] / values['unhealthy_count']
    else:
        u_fraction = 1

    # Until 2022-06-22, unhealthy_unk_count is usually the same as
    # unhealthy_count, or one less.
    if row['date'] < '20220622':
        if values['unhealthy_count'] >= 10:
            assert u_fraction >= 0.8

    assert values['predicted_covid_positive_count'] <= values['unhealthy_unk_count']

    # Estimate of symptomatic prevalence in the population.  If you look at
    # corrected_prevalence_region_*.csv and add it up for a region, it matches
    # the official ZOE prevalence for that region.
    # See output file: region.csv.
    #
    # Although, you could argue there's an issue with the dates.  ZOE regional
    # prevalence is calculated from ZOE regional incidence
    # (see prevalence_from_incidence/).  The date specified for ZOE regional
    # incidence is publish date - 2, not publish date - 1.  Also, regional
    # incidence is based on a 14-day average.
    #
    # If you average it over 8 (!) days for a UTLA, it matches
    # the estimates on the official ZOE map and "watch list".
    # See output file: utla_8d_average.csv.
    #
    # Similarly if you look at corrected_prevalence_age_*.csv and add it up
    # for an age group, it matches the official graphs of UK prevalence rate
    # by age.
    # See output file: age_group_to_covid_rate.csv.
    #
    # (It's as if they endorse their stratification of P_S by region,
    #  and to a lesser degree by age group, but they can't stratify P_S
    #  by both at the same time?)

    # 'factor' is inf for Northern Ireland districts on date == '20220920',
    # when prevalence_history shows 0 for the region, and when
    # the daily report says "Estimate not available", and
    # this cuts a small notch in the UK total prevalence graph on the website.

    if values['unhealthy_unk_count'] == 0 or row['factor'] == 'inf':
        assert row['corrected_covid_positive'] == ''
        values['corrected_covid_positive'] = 0.0
    else:
        read_float('corrected_covid_positive')

    # It is not bounded by population, at least for individual strata.
    #assert values['corrected_covid_positive'] <= values['population']

    if values['unhealthy_unk_count'] == 0:
        assert row['corrected_covid_positive_prob'] == ''
        values['corrected_covid_positive_prob'] = 0.0
    else:
        read_float('corrected_covid_positive_prob')

    # If you look at rows with the same (date, region) in
    # corrected_prevalence_region_*.csv, factor is always the same.
    # The same applies to factor_prob.  Factor_prob is equal to
    # (sum(corrected_covid_positive) / sum(corrected_covid_positive_prob))
    # We check this assertion in main().
    #
    # Corrected_prevalence_age_* does the same except with
    # (date, age_group).
    #
    # The only difference between corrected_prevalence_region_*
    # and corrected_prevalence_age_* are the values of
    # corrected_covid_positive, factor, and factor_prob.
    #
    # The change in factor is proportional to the change in factor_prob.
    read_float('factor')
    read_float('factor_prob')

    if values['predicted_covid_positive_count'] == 0 or values['population'] == 0:
        # This includes all cases where respondent_count == 0, or
        # u_fraction == 0.  In these cases corrected_covid_positive
        # should be unknown, indeed the file shows it as empty (not 0.0).
        # However, ZOE *do* treat it as 0.0 when adding up;
        # this is simplest to implement but could cause issues.
        assert values['corrected_covid_positive'] == 0
    else:
        # factor == (corrected_covid_positive / predicted_covid_positive_count) *
        #           (respondent_count * u_fraction / population)
        assert abs(values['factor'] -
                   (values['corrected_covid_positive'] / values['predicted_covid_positive_count']) *
                   (values['respondent_count'] * u_fraction / values['population'])) < 1e-11

    if values['respondent_count'] == 0 or u_fraction == 0 or values['population'] == 0:
        # So predicted_covid_positive_prob is linked to respondent_count,
        # even though it can be higher (and it can be over 10 times the
        # value of unhealthy_count).
        assert values['predicted_covid_positive_prob'] == 0
        assert values['corrected_covid_positive_prob'] == 0
    else:
        assert abs(values['predicted_covid_positive_prob'] / (values['respondent_count'] * u_fraction) -
                   values['corrected_covid_positive_prob'] / values['population']) < 1e-11

    # Following the pattern above, here's how you scale
    # predicted_covid_positive_count up to the whole population.
    values['+ symptom_based'] = 0
    if values['predicted_covid_positive_count'] != 0:        
        values['+ symptom_based'] = (values['predicted_covid_positive_count'] *
            values['population'] / (values['respondent_count'] * u_fraction))
    
    return values


def parse_file(infile):
    csv_in = csv.DictReader(infile)
    for row in csv_in:
        keys = Keys(*(sys.intern(row[key]) for key in KEY_FIELDS))
        try:
            values = parse_values(row)
        except AssertionError:
            print("ERROR parsing or checking row:")
            print(row)
            print()
            raise
    
        yield Record(keys, values)

def add_values(a, b):
    for (key, value) in b.items():
        if key in ['factor', 'factor_prob']:
            if a[key] != b[key]:
                a[key] == ''
        else:
            a[key] = a[key] + b[key]

# https://www.mikulskibartosz.name/wilson-score-in-python-example/
from math import sqrt
def wilson(p, n, z = 1.96):
    denominator = 1 + z**2/n
    centre_adjusted_probability = p + z*z / (2*n)
    adjusted_standard_deviation = sqrt((p*(1 - p) + z*z / (4*n)) / n)

    lower_bound = (centre_adjusted_probability - z*adjusted_standard_deviation) / denominator
    upper_bound = (centre_adjusted_probability + z*adjusted_standard_deviation) / denominator
    return (lower_bound, upper_bound)

def main(infile, name):
    name = os.path.basename(filename)
    if name.endswith('.csv'):
        name = name[:-len('.csv')]

    # Nested dictionaries: date -> region -> values
    digest_region = {}
    # date -> age_group -> values
    digest_age = {}
    # (region, utla) -> date -> values
    digest_utla = {}
    # (date, imd) -> values
    digest_imd = {}
    # (date, age, imd) -> values
    digest_age_imd = {}

    # lad16cd's don't seem to be unique?  Doesn't matter for our purposes.
    # (region, utla, lad, imd) -> lsoa_count
    digest_lsoa = {}
    # (region, utla, date) -> total population of strata in which
    # corrected_covid_postive_count is well-defined, which requires
    # unhealthy_unk_count > 0.  When there is no information,
    # ZOE assume zero cases.
    digest_utla_defined_pop = {}
    # (region, date) -> defined_pop
    digest_region_defined_pop = {}

    for (keys, values) in parse_file(infile):
        # The column labeled 'gender' obeys the rule defined below.
        # Note this means it is invariant by date.
        #
        # It is actually the number of Lower-layer Super Output Areas
        # for each (region, utla, lad, imd).  The IMD of each ZOE user
        # is estimated from their LSOA.
        keys_lsoa = (keys.region, keys.UTLA19CD, keys.lad16cd, keys.imd)
        lsoa_count = values['gender']

        v = digest_lsoa.get(keys_lsoa, None)
        if v is None:
            v = lsoa_count
            digest_lsoa[keys_lsoa] = v
        else:
            if v != lsoa_count:
                print ("Inconsistent value in field 'gender' (which is not gender)")
                print ("keys = ", keys)
                print ("values = ", values)
                print ("Expected value = ", v)
                sys.exit(1)
        # Get rid of it.
        del values['gender']

        keys_utla_date = (keys.region, keys.UTLA19CD, keys.date)
        v = digest_utla_defined_pop.get(keys_utla_date, None)
        if v is None:
            v = 0
            digest_utla_defined_pop[keys_utla_date] = v
        if values['unhealthy_unk_count'] > 0:
            v += values['population']
            digest_utla_defined_pop[keys_utla_date] = v

        keys_region_date = (keys.region, keys.date)
        v = digest_region_defined_pop.get(keys_region_date, None)
        if v is None:
            v = 0
            digest_region_defined_pop[keys_region_date] = v
        if values['unhealthy_unk_count'] > 0:
            v += values['population']
            digest_region_defined_pop[keys_region_date] = v

        v = digest_region.get(keys.date, None)
        if v is None:
            v = {}
            digest_region[keys.date] = v
        v2 = v.get(keys.region)
        if v2 is None:
            v2 = dict(values)
            v[keys.region] = v2
        else:
            add_values(v2, values)

        v = digest_age.get(keys.date, None)
        if v is None:
            v = {}
            digest_age[keys.date] = v
        v2 = v.get(keys.age_group)
        if v2 is None:
            v2 = dict(values)
            v[keys.age_group] = v2
        else:
            add_values(v2, values)

        keys_utla = (keys.region, keys.UTLA19CD)
        v = digest_utla.get(keys_utla, None)
        if v is None:
            v = {}
            digest_utla[keys_utla] = v
        v2 = v.get(keys.date, None)
        if v2 is None:
            v2 = dict(values)
            v[keys.date] = v2
        else:
            add_values(v2, values)

        keys_imd = (keys.date, keys.imd)
        v = digest_imd.get(keys_imd, None)
        if v is None:
            v = dict(values)
            digest_imd[keys_imd] = v
        else:
            add_values(v, values)

        keys_age_imd = (keys.date, keys.age_group, keys.imd)
        v = digest_age_imd.get(keys_age_imd, None)
        if v is None:
            v = dict(values)
            digest_age_imd[keys_age_imd] = v
        else:
            add_values(v, values)

    value_fields = list(values.keys())
    ZERO_VALUES = {field:0 for field in value_fields}

    outdir = f'out/prevalence_digest/{name}/'
    os.makedirs(outdir, exist_ok=True)

    first_by_age = next(iter(digest_age.values()))
    age_groups = list(first_by_age.keys())

    with open(outdir + 'age.csv', 'w') as outfile:
        csv_out = csv.writer(outfile)
        csv_out.writerow(['date', 'age_group'] + value_fields +
                         ['+ response_rate'])
        for (date, by_age) in digest_age.items():
            for (age_group, values) in by_age.items():
                response_rate = values['respondent_count'] / values['population']
                csv_out.writerow([date, age_group] + list(values.values()) + [response_rate])

    with open(outdir + 'age_group_to_covid_rate.csv', 'w') as outfile:
        csv_out = csv.writer(outfile)
        csv_out.writerow(['date'] + age_groups)
        for (date, by_age) in digest_age.items():
            covid_rates = [values['corrected_covid_positive'] / values['population']
                           for values in by_age.values()]
            csv_out.writerow([date] + covid_rates)

    with open(outdir + 'age_group_to_u_fraction.csv', 'w') as outfile:
        csv_out = csv.writer(outfile)
        csv_out.writerow(['date'] + age_groups)
        for (date, by_age) in digest_age.items():
            u_fractions = [values['unhealthy_unk_count'] / values['unhealthy_count']
                           for values in by_age.values()]
            csv_out.writerow([date] + u_fractions)

    with open(outdir + 'age_group_to_response_rate.csv', 'w') as outfile:
        csv_out = csv.writer(outfile)
        csv_out.writerow(['date'] + age_groups)
        for (date, by_age) in digest_age.items():
            response_rates = [values['respondent_count'] / values['population']
                              for values in by_age.values()]
            csv_out.writerow([date] + response_rates)

    if name.startswith('corrected_prevalence_age_trend_'):
        for (date, by_age) in digest_age.items():
            for (age_group, values) in by_age.items():
                try:
                    if values['factor'] == float('inf'):
                        continue

                    assert values['corrected_covid_positive'] <= values['population']

                    assert abs(values['factor'] -
                        (values['corrected_covid_positive'] / values['+ symptom_based'])) < 1e-11

                    assert abs(values['factor_prob'] -
                        (values['corrected_covid_positive'] / values['corrected_covid_positive_prob'])) < 1e-11
                except AssertionError:
                    print ('Inconsistent values for age_group: ', age_group, date)
                    print (values)
                    raise

    with open(outdir + 'region.csv', 'w') as outfile:
        csv_out = csv.writer(outfile)
        csv_out.writerow(['date', 'region'] + value_fields +
                         ['+ defined_population_fraction'])
        for (date, by_region) in digest_region.items():
            en = dict(ZERO_VALUES)
            uk = dict(ZERO_VALUES)
            for (region, values) in by_region.items():
                key = (region, date)
                defined_pop_fraction = digest_region_defined_pop[key] / values['population']
                csv_out.writerow([date, region] + list(values.values()) +
                                 [defined_pop_fraction])
                add_values(uk, values)
                if region not in ['Wales', 'Scotland', 'Northern Ireland']:
                    add_values(en, values)
            csv_out.writerow([date, 'England'] + list(en.values()))
            csv_out.writerow([date, 'UK'] + list(uk.values()))

    if name.startswith('corrected_prevalence_region_trend_'):
        for (date, by_region) in digest_region.items():
            for (region, values) in by_region.items():
                try:
                    if values['factor'] == float('inf'):
                       continue

                    assert values['corrected_covid_positive'] <= values['population']

                    assert abs(values['factor'] -
                        (values['corrected_covid_positive'] / values['+ symptom_based'])) < 1e-11

                    assert abs(values['factor_prob'] -
                        (values['corrected_covid_positive'] / values['corrected_covid_positive_prob'])) < 1e-11
                except AssertionError:
                    print ('Inconsistent values for region: ', region, date)
                    print (values)
                    raise

    with open(outdir + 'imd.csv', 'w') as outfile:
        csv_out = csv.writer(outfile)
        csv_out.writerow(['date', 'imd'] + value_fields + ['+ response_rate'])
        for ((date, imd), values) in digest_imd.items():
            response_rate = values['respondent_count'] / values['population']
            csv_out.writerow([date, imd] + list(values.values())+ [response_rate])

    with open(outdir + 'age_imd.csv', 'w') as outfile:
        csv_out = csv.writer(outfile)
        csv_out.writerow(['date', 'age_group', 'imd'] + value_fields + ['+ response_rate'])
        for ((date, age_group, imd), values) in digest_age_imd.items():
            response_rate = values['respondent_count'] / values['population']
            csv_out.writerow([date, age_group, imd] + list(values.values()) + [response_rate])

    with open(outdir + 'lsoa_count.csv', 'w') as outfile:
        csv_out = csv.writer(outfile)
        csv_out.writerow(['region', 'UTLA19CD', 'lad16cd', 'imd', '+ LSOA_count'])
        for ((region, utla, lad, imd), lsoa_count) in digest_lsoa.items():
            csv_out.writerow([region, utla, lad, imd, lsoa_count])

    def write_utla_average(name, N):
        with open(name, 'w') as outfile:
            csv_out = csv.writer(outfile)
            csv_out.writerow(['region', 'UTLA19CD', 'date'] +
                            value_fields +
                            ['+ covid_rate',
                             '+ covid_rate_lo', '+ covid_rate_hi'])
            for ((region, utla), by_date) in digest_utla.items():
                by_date = list(by_date.items())
                for i in range(N-1, len(by_date)):
                    totals = dict(ZERO_VALUES)
                    for j in range(i-(N-1), i+1):
                        add_values(totals, by_date[j][1])
                    values = { key:value / N for (key, value) in totals.items() }

                    values['+ covid_rate'] = values['corrected_covid_positive'] / values['population']
                    # TODO comment:
                    # Note lack of u_fraction.  But this is what matches, sigh.
                    # Also, calculating it *after* multiplying by factor sounds
                    # like a big problem to me?
                    (values['+ covid_rate_lo'],
                     values['+ covid_rate_hi']) = (
                        wilson(values['+ covid_rate'],
                            values['respondent_count']))

                    csv_out.writerow([region, utla, by_date[i][0]] + list(values.values()))

    if name.startswith('corrected_prevalence_region_trend_'):
        with open(outdir + 'utla.csv', 'w') as outfile:
            csv_out = csv.writer(outfile)
            csv_out.writerow(['region', 'UTLA19CD', 'date'] + value_fields +
                             ['+ defined_population_fraction'])
            for ((region, utla), by_date) in digest_utla.items():
                for (date, values) in by_date.items():
                    key = (region, utla, date)
                    defined_pop_fraction = digest_utla_defined_pop[key] / values['population']
                    csv_out.writerow([region, utla, date] + list(values.values()) +
                                     [defined_pop_fraction])

        # 8-day average matches estimates on the official map and "watch list".
        # This is an off-by-one error: it is documented as a 7 day average.
        write_utla_average(outdir + 'utla_8d_average.csv', 8)

        # As documented, 14-day average matches the local case graph in the app.
        # But I haven't checked exactly, e.g. it could be a 15-day average :-).
        write_utla_average(outdir + 'utla_14d_average.csv', 14)

#     for ((region, utla), by_date) in digest_utla.items():
#         for (date, values) in by_date.items():
#             try:
#                 # Although this assertion does not hold for individual strata,
#                 # there have not been any breaches in the UTLA totals
#                 # in the region_trend file.  Only in the age_trend file.
#                 #assert values['corrected_covid_positive'] <= values['population']
#                 
#                 # These assertions do *not* hold for UTLA's.
#                 #assert values['predicted_covid_positive_prob'] <= values['respondent_count']
#                 #assert values['predicted_covid_positive_prob'] <= values['unhealthy_count']
#                 #assert values['corrected_covid_positive_prob'] <= values['population']
#             except AssertionError:
#                 print ('Inconsistent values for UTLA: ', region, utla, date)
#                 print (values)
#                 raise


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: ./prevalence_digest.py input.csv")
        print()
        print("Create digests of corrected_prevalence_*_trend_*.csv from covid-public-data")
        print("Output files are written to out/prevalence_digest/")
        sys.exit(2)
    filename = sys.argv[1]
    with (open(filename) as infile):
        main(infile, filename)
