# Shoulder Capsulitis Lab

A transparent, reproducible re-analysis of **two separate** open Mendeley Data deposits from small,
single centre randomised trials in adhesive capsulitis (frozen shoulder), both from Maharishi
Markandeshwar (MM), Mullana, India. Each trial is analysed on its own. **The two are never pooled and
are not one large trial.** Neither trial has a published results paper; only a protocol (Spiral
Stretch) and a conference protocol abstract (magnetotherapy) exist: there is no results paper for either trial.

**Status:** public repository at https://github.com/victorgomezadapty/shoulder-capsulitis-lab. A Kaggle
dataset and notebook are being prepared. There is no dedicated Vercel site for this case. A later portfolio
case is planned (see [PORTFOLIO_BRIEF.md](PORTFOLIO_BRIEF.md)). The dataset creators and protocol authors were
not contacted and have not endorsed this project.

## Main findings

| | Spiral Stretch trial | Magnetotherapy trial |
|-|-|-|
| Deposit | [hnvhm376hg V1](https://data.mendeley.com/datasets/hnvhm376hg/1), 27 Mar 2025 | [khdtg3rzmp V1](https://data.mendeley.com/datasets/khdtg3rzmp/1), 29 May 2026 |
| Comparison | Spiral Stretch + physiotherapy vs physiotherapy | Group 1 vs Group 2 (coding undocumented; Group 1 presumed magnetotherapy + physiotherapy) |
| Dose (protocol) | 4 weeks, 3 sessions per week | 2 weeks, 2 sessions per week |
| n | 24 (12 and 12), ages 30 to 60 | 36 (18 and 18), ages 32 to 60 |
| SPADI, extra improvement in group 1 | +11.2 points (95% bootstrap CI +7.8 to +14.4) | +1.8 points (-1.9 to +5.6) |
| NPRS pain, extra improvement in group 1 | +1.42 points (+1.00 to +1.75) | -0.06 points (-0.61 to +0.50) |
| Flexion, extra improvement in group 1 | +14.2 degrees (+8.2 to +19.8) | -1.0 degrees (-9.7 to +7.6) |
| Every person improved on every outcome | yes, 24 of 24 | yes, 36 of 36 |

**Spiral Stretch:** as deposited, the Spiral Stretch group improved more than the control group on all
seven outcomes, with intervals that exclude zero. But the effect sizes are implausibly large for a
physiotherapy add-on (Hedges g 1.2 to 2.9) because the change scores are extraordinarily regular: every
person's pain fell by 3 to 5 points (9 of 12 in the Spiral group by exactly 5, 8 of 12 controls by exactly
3), and after treatment the two groups' flexion and abduction values do not overlap at all. The contrast
survives dropping the 13 rows with an inconsistent BMI (n=5 + 6) and using the deposited flexion change
with its 5 degree error, but a noise stress test shows it is only as solid as the recorded regularity:
with an extra 1.5 NPRS points of random noise per person, half of the simulated trials lose the pain
difference.

**Magnetotherapy:** both groups improved by almost exactly the same amount on all eight outcomes. No
between group interval excludes zero in the primary analysis. Across 24 sensitivity contrasts (dropping 3
BMI inconsistent rows, keeping only the protocol ages 35 to 50, removing repeated SPADI pairs), one
excludes zero: adduction, after removing repeated SPADI pairs, -2.2 degrees (-4.1 to -0.5) in favour of
Group 2, about what chance alone would produce among 24 tests. The deposit gives no evidence for or
against an added effect of magnetotherapy.

**What can be said:** these are two small single centre deposits with data quality flags and no results
paper. Read them as material for teaching transparent re-analysis, not as evidence that either
intervention works. Full numbers: [RESULTS.md](RESULTS.md).

## Data quality flags (reported, not corrected)

Spiral Stretch (`Spiral Stretch Data.sav`):
* SPSS only, no codebook beyond SPSS value labels (GROUP 1 EXPRIMENTAL, 2 CONTROL; GENDER 1 MALE, 2 FEMALE).
* BMI does not match height and weight in 13 of 24 rows (by more than 0.5 kg/m2, up to 6.6).
* One flexion change score is 5 degrees off (deposited 66, post minus pre 61).
* Every person improves on every outcome; pain falls by 3 to 5 points in all 24.
* The protocol includes diabetic patients only and planned a 12 person pilot. The deposit has n=24 and
  no diabetes variable, so diabetes status cannot be checked.
* An SPSS `filter_$` artifact column (selects GROUP = 1).

Magnetotherapy (`NEW.xlsx`):
* No codebook. GROUP and GENDER codes are undocumented. Body size suggests GENDER 2 may be men (mean
  166.8 cm and 74.9 kg vs 158.9 cm and 57.7 kg for code 1), which would be the opposite of the Spiral
  Stretch labels. This is an inference only; sex is not used in any inference here.
* BMI does not match height and weight in 3 of 36 rows.
* The protocol abstract says ages 35 to 50, but 19 of 36 participants are outside that range.
* The protocol abstract measures pain with VAS; the data use NPRS.
* 4 identical SPADI pre and post pairs are shared by 11 rows (other columns differ).
* Every person improves on every outcome. Change scores are internally consistent.
* Ethics approval and trial registration are not stated in the deposit or the abstract and were not
  verified.

## What this project adds

1. A **data audit** of each deposit, with every flag counted and kept visible.
2. **Separate per trial analyses**: within group change and between group contrasts with bootstrap
   intervals (people resampled within group), Welch intervals, baseline adjusted differences, Hedges g
   and the probability of superiority. Permutation p values are reported as context only.
3. **Sensitivity analyses** aimed at the specific problems found in each file.
4. A **regularity analysis and noise stress test** that make the unusual uniformity of the changes
   explicit, instead of letting it inflate the effect sizes silently.
5. A **side by side picture** of the two trials with no combined estimate.

## What this project is not

* Not a meta-analysis and not a pooled trial. Interventions, doses, variable names and ROM sets differ.
* Not a check of a published result: there is none for either trial.
* Not clinical advice and not evidence of efficacy.
* Not a reuse of the JCDR protocols, which are cited only.

## Project layout

| Path | Content |
|-|-|
| `data/raw/Spiral Stretch Data.sav`, `data/raw/NEW.xlsx` | Official deposit files, unmodified, sha256 checked on every load |
| `data/derived/` | CSV conversions with every column and value unchanged, plus `README.md` |
| `src/shoulder_capsulitis_lab/` | `data` (hashes, per trial harmonisation), `audit`, `stats`, `analysis`, `figures`, `report` |
| `scripts/fetch_data.py` | Copies or downloads the official files and stops on any sha256 mismatch |
| `scripts/run_analysis.py` | Regenerates `data/derived/`, `tables/`, `figures/`, `results/summary.json`, `RESULTS.md` |
| `tests/` | Hashes, sample sizes, no pooling, quality flag counts, key numbers, license and wording checks |
| `tables/` | 11 CSV tables, aggregates only |
| `figures/` | 8 figures as PNG with WebP twins |
| `ANALYSIS_PLAN.md`, `DISCUSSION.md` | Plan and limits, bibliographic notes |
| `PORTFOLIO_BRIEF.md` | Locked facts for a later bilingual portfolio case |

## Reproduce

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/fetch_data.py
.venv/bin/python scripts/run_analysis.py
.venv/bin/python -m pytest -q
```

## Citation and license

Data (CC BY 4.0, https://creativecommons.org/licenses/by/4.0/):

> Physiotherapy, Krishnagopal Mondal; Sharma, Sunita (2025). Impact of the "Spiral Stretch" technique on
> Range, Pain and Disability in individuals with Adhesive Capsulitis. Mendeley Data, V1.
> https://doi.org/10.17632/hnvhm376hg.1

> KUMAR, SAHIL; Pattnaik, Sandeep (2026). Effect of Magneto therapy on Pain, Range of motion, and Function
> in individuals with Shoulder Adhesive Capsulitis. Mendeley Data, V1. https://doi.org/10.17632/khdtg3rzmp.1

"Physiotherapy" in the first creator name is a Mendeley profile name artifact; the protocol author is
Krishna Gopal Mondal. Changes, attribution details and the companion protocols (JCDR, CC BY-NC-ND 4.0,
cited only, nothing reproduced) are in [DATA_LICENSE.md](DATA_LICENSE.md). The dataset creators and the
protocol authors have not endorsed this project. Code: MIT ([LICENSE](LICENSE)), copyright 2026 Víctor
Andrés Gómez López. Provenance: [PROVENANCE.md](PROVENANCE.md).
