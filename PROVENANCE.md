# Data provenance

| Field | Spiral Stretch trial | Magnetotherapy trial |
|-|-|-|
| Repository | Mendeley Data, https://data.mendeley.com/datasets/hnvhm376hg/1 | Mendeley Data, https://data.mendeley.com/datasets/khdtg3rzmp/1 |
| Version DOI | 10.17632/hnvhm376hg.1 | 10.17632/khdtg3rzmp.1 |
| Concept DOI | 10.17632/hnvhm376hg | 10.17632/khdtg3rzmp |
| Versions | V1 only | V1 only |
| Published | 27 Mar 2025 | 29 May 2026 |
| Creators | Physiotherapy, Krishnagopal Mondal; Sharma, Sunita | KUMAR, SAHIL; Pattnaik, Sandeep |
| Institution | Maharishi Markandeshwar Institute of Physiotherapy and Rehabilitation, MM, Mullana | Maharishi Markandeshwar University, Mullana |
| License | CC BY 4.0, open, no DUA, no LICENSE file | CC BY 4.0, open, no DUA, no LICENSE file |
| Official file | `Spiral Stretch Data.sav`, 4862 bytes | `NEW.xlsx`, 13848 bytes |
| sha256 | `61f73cffa6a301cd29097a5adc21c48cadcc563f484cfd92eaa58b2e51be0e3d` | `18c9ee575c8babd2f1da4d137fb970f82e04d53c6158dd914c93776069e10b56` |
| Content | 24 rows by 28 columns, SPSS value labels for GROUP, GENDER and filter_$ | 36 rows by 30 columns, one sheet, no missing values |
| Companion | JCDR 2025;19(5):YK06 to YK09, doi 10.7860/JCDR/2025/76129.20996, protocol, CC BY-NC-ND 4.0, cited only | JCDR 2025;19(Suppl 1): Abstract 125, doi 10.7860/JCDR/2025/80478.21711, conference abstract, CC BY-NC-ND 4.0, cited only |
| Results paper | none found | none found |
| Ethics | IEC of MMIMSR Mullana, project IEC-2994 (per protocol) | not stated in deposit or abstract; not verified |
| Registration | CTRI/2024/08/072699 (the protocol labels it a ClinicalTrials.gov ID, which is wrong) | not stated; not verified |
| Protocol vs deposit | Protocol: diabetic patients only, ages 30 to 60, a 12 person pilot. Deposit: n=24, ages 30 to 60, no diabetes variable | Abstract: ages 35 to 50, VAS, 12 person pilot. Deposit: n=36, ages 32 to 60 (19 outside 35 to 50), NPRS |

## How the local copies were made

The license and redistribution verdict was checked live on 11 Nov 2026 (UTC+3) against the
Mendeley Data public API and pages, DataCite, Crossref, DOAJ and the JCDR PDFs. Fresh copies downloaded that
day were byte identical to the copies cached on 8 Nov 2026, and their sha256 matched the hash published by
Mendeley. On 11 Nov 2026 the fresh copies were **copied** (not moved) into `data/raw/` under their official
file names and the sha256 and size were verified again. The source copies were left untouched.

`scripts/fetch_data.py` repeats this: it copies from the verified local cache when present, otherwise downloads
from the Mendeley public file URLs, and stops on any mismatch.

## Derived files

| File | Source | Rows by columns | Note |
|-|-|-|-|
| `data/derived/spiral_stretch_data_from_sav.csv` | `Spiral Stretch Data.sav` | 24 by 28 | pyreadstat conversion, names and values unchanged |
| `data/derived/magnetotherapy_NEW_from_xlsx.csv` | `NEW.xlsx` | 36 by 30 | pandas and openpyxl conversion, names and values unchanged |

Their sha256 is recorded in `results/summary.json` at each run (it can change with the pandas version). The
tests check that each CSV equals its official source file value by value.

## Rules for this project

1. The two deposits are the only data sources. They are never merged, concatenated for analysis or pooled.
2. Hashes are checked on every load (`shoulder_capsulitis_lab.data.verify_raw`), in the analysis script and in
   the tests. The analysis stops on any mismatch.
3. The JCDR protocols are cited only.
4. Status: local draft. No remote, nothing published, no contact with the authors.
