# Derived CSV files

Written by `scripts/run_analysis.py` (function `shoulder_capsulitis_lab.data.write_derived`). Every column name
and value is unchanged from the official deposit file. These files exist only to make the data readable without
SPSS or Excel. The official files in `data/raw/` stay the reference.

## spiral_stretch_data_from_sav.csv (from `Spiral Stretch Data.sav`)

24 rows, 28 columns. The SPSS file holds no variable labels except for `filter_$`. Value labels exactly as in
the SPSS file (the spelling EXPRIMENTAL is the deposit's own):

| Column | Value labels |
|-|-|
| GROUP | 1 = EXPRIMENTAL, 2 = CONTROL |
| GENDER | 1 = MALE, 2 = FEMALE |
| filter_$ | 0 = Not Selected, 1 = Selected (label "GROUP = 1 (FILTER)"; an SPSS artifact) |

No other codebook exists. Units are not documented; they are read as years, cm, kg, kg/m2, SPADI points,
NPRS points and goniometer degrees. Change columns are post minus pre for ROM and pre minus post for SPADI and
NPRS.

## magnetotherapy_NEW_from_xlsx.csv (from `NEW.xlsx`)

36 rows, 30 columns, one sheet (`Sheet1`). **No codebook exists.** GROUP (1, 2) and GENDER (1, 2) codes are
not documented. This project does not invent a codebook. Its reading, labelled as inference:

* GROUP: reported as Group 1 and Group 2. Group 1 is presumed to be magnetotherapy plus physiotherapy by
  analogy with the Spiral Stretch file from the same department and the order in the abstract. Not confirmed.
* GENDER: code 2 people are on average taller and heavier (166.8 cm, 74.9 kg) than code 1 (158.9 cm,
  57.7 kg), which suggests code 2 may be men, the opposite of the Spiral Stretch labels. Not confirmed and not
  used in any inference.
* `S_FLEXION` and `S_EXTENSION` are read as the baseline values (they pair with `POST_` columns and their
  `POST-PRE` change columns match). `SPADI` is the baseline SPADI; `PRE-POSTSPDAI` (sic) is its change.
