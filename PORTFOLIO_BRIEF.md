# Portfolio brief (locked facts)

For a later portfolio PR. Do not change these facts without re-running the analysis.

## Page and language

* English is the default page, title and Open Graph text. Spanish is available through the portfolio's existing
  one click language switch (the same switch the other Line 2 cases use). No language negotiation from headers,
  cookies or local storage.
* `publicLink`: the GitHub repository, once it exists (planned slug `victorgomezadapty/shoulder-capsulitis-lab`;
  not created yet). No dedicated Vercel site for this case.
* Suggested title: "Shoulder Capsulitis Lab · Two small open trials, re-analysed separately". Spanish:
  "Shoulder Capsulitis Lab · Dos ensayos abiertos pequeños, reanalizados por separado".

## One line

English: A transparent re-analysis of two separate open Mendeley trials in frozen shoulder: the Spiral Stretch
deposit shows a large advantage that rests on unusually regular data, while the magnetotherapy deposit shows no
difference between groups.

Spanish: Un reanálisis transparente de dos ensayos abiertos de Mendeley, por separado, en hombro congelado: el
depósito de Spiral Stretch muestra una ventaja grande que se apoya en datos inusualmente regulares, y el de
magnetoterapia no muestra diferencias entre grupos.

## Locked facts

* Spiral Stretch: Mendeley Data hnvhm376hg V1, doi 10.17632/hnvhm376hg.1, CC BY 4.0; creators Physiotherapy,
  Krishnagopal Mondal; Sharma, Sunita. n=24 (12 and 12), ages 30 to 60, 10 men and 14 women. 4 weeks, 3 sessions
  per week.
* Spiral Stretch minus control improvement: SPADI +11.2 points (+7.8 to +14.4); NPRS +1.42 (+1.00 to +1.75);
  flexion +14.2 degrees (+8.2 to +19.8); Hedges g 1.2 to 2.9 across 7 outcomes.
* Spiral Stretch flags: BMI inconsistent in 13 of 24 rows; one flexion change 5 degrees off; every person improved
  on every outcome; pain fell 3 to 5 points in all 24; protocol says diabetic only and a 12 person pilot, deposit
  has n=24 and no diabetes variable; registration CTRI/2024/08/072699, ethics IEC-2994.
* Noise stress test: with 1.5 NPRS points of added noise per person, about half of simulated trials lose the pain
  difference.
* Magnetotherapy: Mendeley Data khdtg3rzmp V1, doi 10.17632/khdtg3rzmp.1, CC BY 4.0; creators KUMAR, SAHIL;
  Pattnaik, Sandeep. n=36 (18 and 18), ages 32 to 60. 2 weeks, 2 sessions per week.
* Magnetotherapy Group 1 minus Group 2: SPADI +1.8 (-1.9 to +5.6); NPRS -0.06 (-0.61 to +0.50); flexion -1.0
  (-9.7 to +7.6); no primary interval excludes zero in 8 outcomes; 1 of 24 sensitivity contrasts does
  (adduction after removing repeated SPADI pairs, -2.2 degrees, -4.1 to -0.5, favouring Group 2).
* Magnetotherapy flags: no codebook (group and sex codes undocumented); BMI inconsistent in 3 of 36; 19 of 36
  outside the protocol ages 35 to 50; VAS in the protocol, NPRS in the data; ethics and registration unverified.

## Must always be said

* Two separate trials, never pooled, not one large RCT. Both small and single centre (MM, Mullana, India).
* No results paper exists for either trial.
* The JCDR protocols are cited only (CC BY-NC-ND 4.0); nothing from them is reproduced.
* The dataset creators and protocol authors have not endorsed this work.
* Not evidence that either treatment works.

## Figures for the case (English labels, PNG and WebP)

`fig02_two_separate_trials`, `fig03_spiral_before_after`, `fig05_between_group_side_by_side`, `fig06_regularity`,
`fig08_spiral_noise_stress`. Captions should carry the CC BY 4.0 credit line in the figure footer.

## Status

Local draft only. No GitHub repo, no Kaggle page, no Vercel project, nothing published, no contact with authors.
