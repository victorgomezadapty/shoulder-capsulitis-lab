# Data license and attribution

This project uses exactly two datasets. They are separate deposits of separate trials and are licensed,
attributed and analysed separately.

## Dataset 1: Spiral Stretch trial

> Physiotherapy, Krishnagopal Mondal; Sharma, Sunita (2025). Impact of the "Spiral Stretch" technique on
> Range, Pain and Disability in individuals with Adhesive Capsulitis. Mendeley Data, V1.
> https://doi.org/10.17632/hnvhm376hg.1. Licensed CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/).

* Creators in official order: "Krishnagopal Mondal Physiotherapy" (Mendeley profile name; DataCite renders it
  "Physiotherapy, Krishnagopal Mondal"), then Sunita Sharma. "Physiotherapy" is a profile name artifact; the
  protocol author is Krishna Gopal Mondal. The official deposit attribution is kept as is.
* License: Creative Commons Attribution 4.0 International. Access open. No LICENSE file in the deposit, no
  data use agreement, no extra terms. Mendeley card and DataCite agree.
* File: `data/raw/Spiral Stretch Data.sav`, unmodified.

## Dataset 2: Magnetotherapy trial

> KUMAR, SAHIL; Pattnaik, Sandeep (2026). Effect of Magneto therapy on Pain, Range of motion, and Function in
> individuals with Shoulder Adhesive Capsulitis. Mendeley Data, V1. https://doi.org/10.17632/khdtg3rzmp.1.
> Licensed CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/).

* Creators in official order: SAHIL KUMAR; Sandeep Pattnaik (Maharishi Markandeshwar University, Mullana).
* License: Creative Commons Attribution 4.0 International. Access open. No LICENSE file, no data use
  agreement. Mendeley card and DataCite agree.
* File: `data/raw/NEW.xlsx`, unmodified.

## Changes made (CC BY 4.0 section 3(a)(1)(B))

* The two deposited files are kept byte identical and are sha256 checked on every load.
* `data/derived/spiral_stretch_data_from_sav.csv`: the SPSS file converted to CSV with pyreadstat. All 24 rows
  and 28 columns, names and values unchanged. SPSS value labels are listed in `data/derived/README.md`.
* `data/derived/magnetotherapy_NEW_from_xlsx.csv`: the single Excel sheet saved as CSV. All 36 rows and 30
  columns, names and values unchanged.
* In memory only: columns renamed to a per trial project scheme; change scores recomputed from pre and post
  values (the deposited change scores are kept and compared); BMI recomputed from height and weight for the
  audit. No rows were added, removed or edited in any file. Sensitivity analyses drop rows in memory only.
* Aggregation and statistical analysis. Tables, figures, `results/summary.json` and `RESULTS.md` are derived
  from these datasets and shared under CC BY 4.0 with the attributions above.
* The two datasets are never merged or pooled.

The dataset creators and the licensor do not endorse this project or its interpretation. No endorsement is
implied.

## Companion publications (different license, cited only)

* Mondal KG, Sharma S, Chatterjee S. Impact of Spiral Stretch Technique on Range of Motion, Pain, and
  Disability in Patients with Adhesive Capsulitis: A Study Protocol for a Randomised Clinical Trial. J Clin
  Diagn Res. 2025 May;19(5):YK06 to YK09. https://doi.org/10.7860/JCDR/2025/76129.20996
* Kumar S, Pattnaik S. Assessing the Efficacy of Magnetotherapy in Individuals with Adhesive Capsulitis: A
  Study Protocol. J Clin Diagn Res. 2025 Sep;19(Suppl 1): Abstract 125. https://doi.org/10.7860/JCDR/2025/80478.21711

Both are CC BY-NC-ND 4.0 (per DOAJ) and the journal holds copyright. They are cited only. No text, tables or
figures from them are reproduced here; only short factual items (design, dose, age range, scale names, ethics
and registration identifiers) are stated in our own words to explain the contradictions with the deposits.
The protocol authors have not endorsed this project.

## Privacy

No names, identifiers, dates or locations are in either file. Quasi identifiers are age, sex, height and weight
at one known centre; the risk is low. No participant is under 18 (youngest 30 and 32). The Spiral Stretch
protocol implies all participants were diabetic, but no diabetes variable is in the data. Author contact
details are not reproduced anywhere in this project.

## Future redistribution

Under CC BY 4.0, the official individual level files are redistributed unmodified in this public GitHub
repository (and later on Kaggle) with the attribution above, the license link and this list of changes.

## Not used

Mendeley r93nz95zc7 (Fernández-López, 2021) is excluded: the population has rotator cuff injuries, not adhesive
capsulitis. An unverified figshare candidate (10.6084/m9.figshare.34936839) was not checked or used.

## Code

MIT License (see `LICENSE`), copyright 2026 Víctor Andrés Gómez López. The MIT license does not apply to the
data or to derived results.
