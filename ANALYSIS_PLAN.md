# Analysis plan

Written on 11 Nov 2026, after the license check and a first look at the files (row counts, column names, BMI and
change score consistency, the spread of pain changes). It is **not** a pre-registered plan: some descriptive
values were seen before it was written. It fixes the definitions and the order of analyses before the reported
contrasts and intervals were produced, and it records every analysis that is reported.

## Principle: two trials, two analyses

The Spiral Stretch deposit (hnvhm376hg) and the magnetotherapy deposit (khdtg3rzmp) are different trials with
different interventions, doses (4 weeks at 3 sessions per week vs 2 weeks at 2 per week), variable names and ROM
sets. Every analysis is run on one trial at a time (`analysis.assert_single_trial`). No rows are combined, no
combined treatment effect is computed, and no figure or table contains a pooled estimate. A side by side table of
standardised effects is allowed for visual comparison only.

## Definitions

* Improvement (positive = better): post minus pre for every ROM direction; pre minus post for SPADI and NPRS.
  Recomputed from the deposited pre and post values. Deposited change scores are kept and compared.
* Groups: Spiral Stretch GROUP 1 = experimental (Spiral Stretch plus physiotherapy), 2 = control, from the SPSS
  value labels. Magnetotherapy GROUP 1 and 2 as coded; Group 1 presumed magnetotherapy plus physiotherapy,
  labelled as an inference.
* Contrast: group 1 minus group 2 mean improvement.

## Primary analysis (per trial, per outcome)

1. Within group mean improvement with a 95% percentile bootstrap interval (10000 resamples, people resampled).
2. Between group difference in mean improvement, 95% percentile bootstrap interval with people resampled within
   their own group (10000 resamples, seed 20261111).
3. Context, not decision rules: Welch 95% interval; baseline adjusted difference (OLS of improvement on group and
   baseline value) with a bootstrap interval; Hedges g with a bootstrap interval; probability of superiority;
   Hodges Lehmann shift; two sided Monte Carlo permutation p value (20000 permutations).

There is no single primary outcome because neither deposit documents one in a results paper. SPADI is listed
first as the disability measure; all outcomes are reported, so readers can see the whole pattern. With 12 or 18
people per group, p values are not used to declare success.

## Audit (reported before any contrast)

Counts of: BMI not matching weight over height squared by more than 0.5 kg/m2; deposited change scores not equal
to the recomputed change (tolerance 0.011); ages outside the protocol range; missing values; exact duplicate rows;
repeated SPADI pre and post pairs; repeated height and weight; people improving on every outcome; NPRS change
range; codebook availability; protocol vs deposit contradictions.

## Sensitivity analyses

Spiral Stretch:
* S1: keep only rows with a consistent BMI (drops 13 of 24 rows).
* S2: use the deposited change scores (keeps the 5 degree flexion error).
* Regularity: SD of improvement relative to SD at baseline, distinct values, ranges after treatment, group overlap.
* Noise stress test: add independent normal noise to each person's improvement and record how often the Welch
  interval still excludes zero (400 simulations per noise level).

Magnetotherapy:
* S1: keep only rows with a consistent BMI (drops 3 of 36).
* S2: keep only the protocol ages 35 to 50 (drops 19 of 36).
* S3: keep only the first occurrence of each repeated SPADI pre and post pair.
* Regularity, as above.

BMI is not an outcome, so the BMI sensitivity asks whether rows with an inconsistent body size record carry the
result, not whether BMI changes it.

## Not done, on purpose

* No pooling, meta-analysis or combined effect.
* No subgroup analysis by sex (Spiral: small cells; magnetotherapy: codes undocumented).
* No modelling of diabetes (no variable).
* No imputation (no missing values).
