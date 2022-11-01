#!/usr/bin/env python3
#
# If you can use pypy3, this program will run slightly faster.  Heh.
#
# This program relies on dicts preserving insertion order,
# as guaranteed since python 3.7.
#
# We also assume input lines are in a convenient order.

import csv
import os
import os.path
import sys
from collections import namedtuple

KEYS = [
    'date',         # publish date - 1.
    'region',       # large region, originally based on the England NHS regions.
    'UTLA19CD',     # upper tier local authority
    'lad16cd',      # local authority district
    'age_group',    # age group
    'imd']          # index of material deprivation (1 to 3)
Keys = namedtuple('Keys', KEYS)

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

    # Number of responses.  From unique users over the last N days.
    # Comparing the other time series shows that 1 < N < 14.
    #
    # Based on the "hotspots" paper, N might equal 7.
    # That would be consistent with recent daily PDF reports:
    # "based on the most recent report for each contributor
    # that logged during the previous 7 days".
    read_int('respondent_count')

    # Number of users who responded as "unwell".
    read_int('unhealthy_count')

    # Used in u_fraction, see below.  Not clear why.
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

    # I can think of one hypothesis for unhealthy_unk_count.
    # Over June, ZOE transitioned to a different reporting UI.
    # It requires some user setup:
    # https://health-study.joinzoe.com/post/new-daily-report-usual-self
    #
    # Initially, new-style reports were not used in published estimates.
    # At the same time we saw sharp drops in the number of reports used
    # in the data files ("active_users").
    #
    # From the daily PDF report.
    # 2022-06-22: From 22nd June, the new symptom reporting flow is available to 100%
    # of App users who consented to the ZOE Health Study. We have fully migrated the
    # COVID figures to the new symptom reporting flow and from this day, we compute
    # our estimates on 100% of the eligible user base, except for local prevalence figures
    # which are smoothed over two weeks and they will be gradually including more
    # users.
    #
    # I don't see the new system on my phone.  Either I declined to set it up,
    # or I declined to agree to some new research consent as a pre-requisite.
    # However I can still make reports.
    #
    # You might think unhealthy_count includes all "unhealthy" reports, and
    # unhealthy_unk_count includes only new-style reports.
    #
    # However, that wouldn't explain why u_fraction would be low e.g. 20% overall,
    # 12% in the 35-54 age group.  And why it *fell* during the first week,
    # or why it stays nearly 100% for 0-17.  According to the blog, 0-17 can
    # only be reported by an adult on their behalf, and this process does not
    # use the new UI...
    #
    # Revised hypothesis: unhealthy_unk_count includes only *old* style reports.
    # This sounds undesirable for the official UTLA estimates.
    #
    # This still doesn't explain why we appear to use respondent_count * u_fraction
    # as a denominator (see below).  I.e. why wouldn't the denominator just be the
    # total number of reports from users who didn't opt in to the new UI?
    # It's as if that number is somehow not available, and we're using a crude
    # approximation instead.

    if values['unhealthy_count']:
        u_fraction = values['unhealthy_unk_count'] / values['unhealthy_count']
    else:
        u_fraction = 1

    # unhealthy_unk_count is usually the same as unhealthy_count, or one less
    # ... until 2022-06-22.
    if row['date'] < '20220622':
        if values['unhealthy_count'] >= 10:
            assert u_fraction >= 0.8

    assert values['predicted_covid_positive_count'] <= values['unhealthy_unk_count']

    # Estimate of symptomatic prevalence in the population.  If you look at
    # corrected_prevalence_region_*.csv and add it up for a region, it matches
    # the official ZOE prevalence for that region.
    #
    # Although the date is off by one day IMO.  ZOE regional prevalence is
    # calculated from ZOE regional incidence (see prevalence_from_incidence/).
    # The date specified for ZOE regional incidence is publish date - 2,
    # not publish date - 1.
    #
    # If you average it over 8 (!) days for a UTLA, it matches
    # the official ZOE prevalence for that UTLA.
    #
    # I think if you look at corrected_prevalence_age_*.csv and add it up
    # for an age group, it matches the official graphs of UK prevalence by age.

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

    # Is it theoretically possible for 'factor_prob' to be 'inf' as well?
    if values['unhealthy_unk_count'] == 0:
        assert row['corrected_covid_positive_prob'] == ''
        values['corrected_covid_positive_prob'] = 0.0
    else:
        read_float('corrected_covid_positive_prob')

    # Sometimes it is several times higher than population, at least for individual strata.
    #assert values['corrected_covid_positive_prob'] <= values['population']

    if values['respondent_count'] == 0 or u_fraction == 0:
        assert values['predicted_covid_positive_prob'] == 0
        assert values['corrected_covid_positive_prob'] == 0
    else:
        assert abs(values['predicted_covid_positive_prob'] / (values['respondent_count'] * u_fraction) -
                   values['corrected_covid_positive_prob'] / values['population']) < 1e-11

        # So predicted_covid_positive_prob is not bounded by unhealthy_count -
        # because it isn't bounded by respondent_count.
        #assert values['predicted_covid_positive_prob'] <= values['respondent_count']
        #assert values['predicted_covid_positive_prob'] <= values['unhealthy_count']

    # If you look at rows with the same (date, region) in
    # corrected_prevalence_region_*.csv, factor is always the same.
    # The same applies to factor_prob.  Factor_prob is equal to
    # (sum(corrected_covid_positive) / sum(corrected_covid_positive_prob))
    # We check this assertion in main().
    #
    # I think corrected_prevalence_age_* does the same except with
    # (date, age_group).
    #
    # (It's as if they endorse their stratification of P_S by region,
    #  and to a lesser degree by age group, but they can't stratify P_S
    #  by both at the same time?)
    #
    # The only difference between corrected_prevalence_region_*
    # and corrected_prevalence_age_* are the values of
    # corrected_covid_positive, factor, and factor_prob.
    #
    # The change in factor is proportional to the change in factor_prob.
    read_float('factor')
    read_float('factor_prob')
    assert values['factor'] > 0
    assert values['factor_prob'] > 0

    if values['predicted_covid_positive_count'] == 0:
        assert values['corrected_covid_positive'] == 0
    else:
        assert abs(values['factor'] -
                   (values['corrected_covid_positive'] / values['predicted_covid_positive_count']) *
                   (values['respondent_count'] * u_fraction / values['population'])) < 1e-11

    # Based on the above, here's how you scale predicted_covid_positive_count
    # up to the whole population.
    values['+ symptom_based'] = 0
    if values['predicted_covid_positive_count'] != 0:        
        values['+ symptom_based'] = (values['predicted_covid_positive_count'] *
            values['population'] / (values['respondent_count'] * u_fraction))
    
    return values


def parse_file(infile):
    csv_in = csv.DictReader(infile)
    for row in csv_in:
        keys = Keys(*(sys.intern(row[key]) for key in KEYS))
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
    digest_date_region = {}
    # (date, age_group) -> values
    digest_age = {}
    # Nested dictionaries: (region, utla) -> date -> values
    digest_utla = {}

    digest_imd = {}
    digest_age_imd = {}

    for (keys, values) in parse_file(infile):
        if keys.date not in digest_date_region:
            digest_date_region[keys.date] = {}
        if keys.region not in digest_date_region[keys.date]:
            digest_date_region[keys.date][keys.region] = dict(values)
        else:
            add_values(digest_date_region[keys.date][keys.region], values)

        keys_age = (keys.date, keys.age_group)
        if keys_age not in digest_age:
            digest_age[keys_age] = dict(values)
        else:
            add_values(digest_age[keys_age], values)

        keys_utla = (keys.region, keys.UTLA19CD)
        if keys_utla not in digest_utla:
            digest_utla[keys_utla] = {}
        if keys.date not in digest_utla[keys_utla]:
            digest_utla[keys_utla][keys.date] = dict(values)
        else:
            add_values(digest_utla[keys_utla][keys.date], values)

        keys_imd = (keys.date, keys.imd)
        if keys_imd not in digest_imd:
            digest_imd[keys_imd] = dict(values)
        else:
            add_values(digest_imd[keys_imd], values)

        keys_age_imd = (keys.date, keys.age_group, keys.imd)
        if keys_age_imd not in digest_age_imd:
            digest_age_imd[keys_age_imd] = dict(values)
        else:
            add_values(digest_age_imd[keys_age_imd], values)
        
    value_fields = list(values.keys())
    ZERO_VALUES = {field:0 for field in value_fields}

    outdir = f'out/prevalence_digest/{name}/'
    os.makedirs(outdir, exist_ok=True)

    with open(outdir + 'age.csv', 'w') as outfile:
        csv_out = csv.writer(outfile)
        csv_out.writerow(['date', 'age_group'] + value_fields) # + ['+ respondents_per_population')
        for ((date, age_group), values) in digest_age.items():
            #per = values['respondents'] / values['population']
            csv_out.writerow([date, age_group] + list(values.values()))

    if name.startswith('corrected_prevalence_age_trend_'):
        for ((date, age_group), values) in digest_age.items():
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
        csv_out.writerow(['date', 'region'] + value_fields)
        for (date, by_region) in digest_date_region.items():
            en = dict(ZERO_VALUES)
            uk = dict(ZERO_VALUES)
            for (region, values) in by_region.items():
                csv_out.writerow([date, region] + list(values.values()))
                add_values(uk, values)
                if region not in ['Wales', 'Scotland', 'Northern Ireland']:
                    add_values(en, values)
            csv_out.writerow([date, 'England'] + list(en.values()))
            csv_out.writerow([date, 'UK'] + list(uk.values()))

    if name.startswith('corrected_prevalence_region_trend_'):
        for (date, by_region) in digest_date_region.items():
            for (region, values) in by_region.items():
                try:
                    if values['factor'] == float('inf'):
                       continue

                    assert values['corrected_covid_positive'] <= values['population']

                    assert abs(values['factor_prob'] -
                        (values['corrected_covid_positive'] / values['corrected_covid_positive_prob'])) < 1e-11

                    assert abs(values['factor'] -
                        (values['corrected_covid_positive'] / values['+ symptom_based'])) < 1e-11
                except AssertionError:
                    print ('Inconsistent values for region: ', region, date)
                    print (values)
                    raise

    del digest_date_region
    del digest_age

    # 8-day average, as used by official UTLA estimates.
    with open(outdir + 'utla_8d_average.csv', 'w') as outfile:
        csv_out = csv.writer(outfile)
        csv_out.writerow(['region', 'UTLA19CD', 'date'] +
                         value_fields +
                         ['+ percent',
                          '+ percent_lo', '+ percent_hi'])
        for ((region, utla), by_date) in digest_utla.items():
            by_date = list(by_date.items())
            
            N=8
            for i in range(N-1, len(by_date)):
                totals = dict(ZERO_VALUES)
                for j in range(i-(N-1), i+1):
                    add_values(totals, by_date[j][1])
                values = { key:value / N for (key, value) in totals.items() }

                values['+ percent'] = values['corrected_covid_positive'] / values['population']
                # Note lack of u_fraction.  But this is what matches, sigh.
                # Also, calculating it *after* multiplying by factor sounds
                # like a really big problem to me?
                (values['+ percent_lo'],
                 values['+ percent_hi']) = (
                    wilson(values['+ percent'],
                           values['respondent_count']))

                csv_out.writerow([region, utla, by_date[i][0]] + list(values.values()))

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

#    with open('out/prevalence_digest/utla.csv', 'w') as outfile:
#        csv_out = csv.writer(outfile)
#        csv_out.writerow(['region', 'UTLA19CD', 'date'] + value_fields)
#        for ((region, utla), by_date) in digest_utla.items():
#            for (date, values) in by_date.items():
#                csv_out.writerow([region, utla, date] + list(values.values()))

    del digest_utla

    with open(outdir + 'imd.csv', 'w') as outfile:
        csv_out = csv.writer(outfile)
        csv_out.writerow(['date', 'imd'] + value_fields) # + ['+ respondents_per_population')
        for ((date, imd), values) in digest_imd.items():
            #per = values['respondents'] / values['population']
            csv_out.writerow([date, imd] + list(values.values()))
    del digest_imd

    with open(outdir + 'age_imd.csv', 'w') as outfile:
        csv_out = csv.writer(outfile)
        csv_out.writerow(['date', 'age_group', 'imd'] + value_fields) # + ['+ respondents_per_population')
        for ((date, age_group, imd), values) in digest_age_imd.items():
            #per = values['respondents'] / values['population']
            csv_out.writerow([date, age_group, imd] + list(values.values()))
    del digest_age_imd



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
