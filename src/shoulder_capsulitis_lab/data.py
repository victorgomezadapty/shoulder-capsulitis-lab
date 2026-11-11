"""Pinned official files, hash checks, loading and per trial harmonisation.

The two deposits are separate trials. Each is loaded, checked and analysed on its own. There is
deliberately no function in this package that concatenates or merges rows from the two trials.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
DERIVED_DIR = ROOT / "data" / "derived"


@dataclass(frozen=True)
class Outcome:
    key: str          # short project key, e.g. "SPADI"
    label: str        # English label for tables and figures
    unit: str
    pre: str          # deposited column name, baseline
    post: str         # deposited column name, after treatment
    change: str       # deposited change score column
    better: int       # +1 if a higher value is better (ROM), -1 if lower is better (pain, disability)
    deposited_sign: int  # deposited change = deposited_sign * (post - pre)


@dataclass(frozen=True)
class Trial:
    key: str
    short: str
    title: str
    file_name: str
    size: int
    sha256: str
    doi: str
    concept_doi: str
    url: str
    published: str
    creators: str
    citation: str
    companion: str
    intervention: str
    dose: str
    group_labels: dict
    group_coding_documented: bool
    n_expected: int
    n_per_group: tuple
    outcomes: tuple = field(default_factory=tuple)


SPIRAL = Trial(
    key="spiral",
    short="Spiral Stretch trial",
    title='Impact of the "Spiral Stretch" technique on Range, Pain and Disability in individuals with Adhesive Capsulitis',
    file_name="Spiral Stretch Data.sav",
    size=4862,
    sha256="61f73cffa6a301cd29097a5adc21c48cadcc563f484cfd92eaa58b2e51be0e3d",
    doi="10.17632/hnvhm376hg.1",
    concept_doi="10.17632/hnvhm376hg",
    url="https://data.mendeley.com/datasets/hnvhm376hg/1",
    published="2025-03-27",
    creators="Physiotherapy, Krishnagopal Mondal; Sharma, Sunita",
    citation=('Physiotherapy, Krishnagopal Mondal; Sharma, Sunita (2025). Impact of the "Spiral Stretch" technique on '
              "Range, Pain and Disability in individuals with Adhesive Capsulitis. Mendeley Data, V1. "
              "https://doi.org/10.17632/hnvhm376hg.1"),
    companion=("Mondal KG, Sharma S, Chatterjee S. Impact of Spiral Stretch Technique on Range of Motion, Pain, and "
               "Disability in Patients with Adhesive Capsulitis: A Study Protocol for a Randomised Clinical Trial. "
               "J Clin Diagn Res. 2025 May;19(5):YK06 to YK09. doi:10.7860/JCDR/2025/76129.20996"),
    intervention="Spiral Stretch plus conventional physiotherapy vs conventional physiotherapy",
    dose="4 weeks, 3 sessions per week (protocol)",
    group_labels={1: "Spiral Stretch + PT", 2: "Control (PT)"},
    group_coding_documented=True,
    n_expected=24,
    n_per_group=(12, 12),
    outcomes=(
        Outcome("SPADI", "SPADI total (0 to 100)", "points", "SPADI_PRE", "SPADI_POST", "SPADI_CHANGE", -1, -1),
        Outcome("NPRS", "Pain, NPRS (0 to 10)", "points", "NPRS_PRE", "NPRS_POST", "NPRS_CHANGE", -1, -1),
        Outcome("FLEX", "Flexion ROM", "degrees", "SROM_FLE_PRE", "SROM_FLE_POST", "SROM_FLE_CHANGE", 1, 1),
        Outcome("EXT", "Extension ROM", "degrees", "SROM_EXT_PRE", "SROM_EXT_POST", "SROM_EXT_CHANGE", 1, 1),
        Outcome("ABD", "Abduction ROM", "degrees", "SROM_ABD_PRE", "SROM_ABD_POST", "SROM_ABD_CHANGE", 1, 1),
        Outcome("IR", "Internal rotation ROM", "degrees", "SROM_INR_PRE", "SROM_INR_POST", "SROM_INR_CHANGE", 1, 1),
        Outcome("ER", "External rotation ROM", "degrees", "SROM_EXR_PRE", "SROM_EXR_POST", "SROM_EXR_CHANGE", 1, 1),
    ),
)

MAGNETO = Trial(
    key="magneto",
    short="Magnetotherapy trial",
    title="Effect of Magneto therapy on Pain, Range of motion, and Function in individuals with Shoulder Adhesive Capsulitis",
    file_name="NEW.xlsx",
    size=13848,
    sha256="18c9ee575c8babd2f1da4d137fb970f82e04d53c6158dd914c93776069e10b56",
    doi="10.17632/khdtg3rzmp.1",
    concept_doi="10.17632/khdtg3rzmp",
    url="https://data.mendeley.com/datasets/khdtg3rzmp/1",
    published="2026-05-29",
    creators="KUMAR, SAHIL; Pattnaik, Sandeep",
    citation=("KUMAR, SAHIL; Pattnaik, Sandeep (2026). Effect of Magneto therapy on Pain, Range of motion, and Function "
              "in individuals with Shoulder Adhesive Capsulitis. Mendeley Data, V1. https://doi.org/10.17632/khdtg3rzmp.1"),
    companion=("Kumar S, Pattnaik S. Assessing the Efficacy of Magnetotherapy in Individuals with Adhesive Capsulitis: "
               "A Study Protocol. J Clin Diagn Res. 2025 Sep;19(Suppl 1): Abstract 125. doi:10.7860/JCDR/2025/80478.21711"),
    intervention="Magnetotherapy plus conventional physiotherapy vs conventional physiotherapy (group coding not documented)",
    dose="2 weeks, 2 sessions per week (protocol abstract)",
    group_labels={1: "Group 1 (presumed magnetotherapy + PT)", 2: "Group 2 (presumed control)"},
    group_coding_documented=False,
    n_expected=36,
    n_per_group=(18, 18),
    outcomes=(
        Outcome("SPADI", "SPADI total (0 to 100)", "points", "SPADI", "POST_SPADI", "PRE-POSTSPDAI", -1, -1),
        Outcome("NPRS", "Pain, NPRS (0 to 10)", "points", "PRENPRS", "POST_NPRS", "PRE-POSTNPRS", -1, -1),
        Outcome("FLEX", "Flexion ROM", "degrees", "S_FLEXION", "POST_FLEXION", "POST-PREFLEXION", 1, 1),
        Outcome("EXT", "Extension ROM", "degrees", "S_EXTENSION", "POST_EXTENSION", "POST-PREEXTENSION", 1, 1),
        Outcome("ABD", "Abduction ROM", "degrees", "PRE_ABDUCTION", "POST_ABDUCTION", "POST-PREABDUCTION", 1, 1),
        Outcome("ADD", "Adduction ROM", "degrees", "PRE_ADDUCTION", "POST_ADDUCTION", "POST-PREADDUCTION", 1, 1),
        Outcome("IR", "Internal rotation ROM", "degrees", "PRE_IR", "POST_IR", "POST-PREIR", 1, 1),
        Outcome("ER", "External rotation ROM", "degrees", "PRE_ER", "POST_ER", "POST-PREER", 1, 1),
    ),
)

TRIALS = {SPIRAL.key: SPIRAL, MAGNETO.key: MAGNETO}
EXPECTED_RAW = sorted(t.file_name for t in TRIALS.values())
DERIVED_NAMES = {"spiral": "spiral_stretch_data_from_sav.csv", "magneto": "magnetotherapy_NEW_from_xlsx.csv"}


def sha256sum(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_raw(raw_dir: Path | None = None) -> dict:
    """Check size and sha256 of both official files. Raise ValueError on any mismatch."""
    raw_dir = Path(raw_dir) if raw_dir else RAW_DIR
    out = {}
    for t in TRIALS.values():
        p = raw_dir / t.file_name
        if not p.exists():
            raise ValueError(f"missing official file: {p.name}")
        size = p.stat().st_size
        digest = sha256sum(p)
        if size != t.size or digest != t.sha256:
            raise ValueError(f"{p.name}: size {size} sha256 {digest} does not match the pinned deposit file")
        out[t.file_name] = digest
    return out


def load_raw(trial: str, raw_dir: Path | None = None):
    """Return (DataFrame exactly as deposited, metadata dict). Verifies hashes first."""
    raw_dir = Path(raw_dir) if raw_dir else RAW_DIR
    verify_raw(raw_dir)
    t = TRIALS[trial]
    p = raw_dir / t.file_name
    if trial == "spiral":
        import pyreadstat
        df, meta = pyreadstat.read_sav(str(p))
        return df, {"value_labels": meta.variable_value_labels, "column_labels": meta.column_names_to_labels}
    df = pd.read_excel(p, sheet_name=0)
    import openpyxl
    wb = openpyxl.load_workbook(p, read_only=True)
    return df, {"sheets": wb.sheetnames, "value_labels": {}, "column_labels": {}}


def prepare(trial: str, raw: pd.DataFrame) -> pd.DataFrame:
    """Per trial analysis frame. Recomputes change scores from pre and post; keeps deposited ones too.

    `imp_<KEY>` is the improvement (positive = better): post minus pre for ROM, pre minus post for
    SPADI and NPRS. `dep_<KEY>` is the deposited change score in the same improvement direction.
    """
    t = TRIALS[trial]
    df = pd.DataFrame({
        "trial": t.key,
        "row": np.arange(1, len(raw) + 1),
        "group": raw["GROUP"].astype(int),
        "age": raw["AGE"].astype(float),
        "sex_code": raw["GENDER"].astype(int),
        "height_cm": raw["HEIGHT"].astype(float),
        "weight_kg": raw["WEIGHT"].astype(float),
        "bmi_deposited": raw["BMI"].astype(float),
    })
    df["bmi_recomputed"] = df.weight_kg / (df.height_cm / 100) ** 2
    df["bmi_abs_diff"] = (df.bmi_deposited - df.bmi_recomputed).abs()
    for o in t.outcomes:
        df[f"pre_{o.key}"] = raw[o.pre].astype(float)
        df[f"post_{o.key}"] = raw[o.post].astype(float)
        df[f"imp_{o.key}"] = o.better * (df[f"post_{o.key}"] - df[f"pre_{o.key}"])
        dep = raw[o.change].astype(float)
        # deposited change = deposited_sign * (post - pre); improvement direction = better * (post - pre)
        df[f"dep_{o.key}"] = dep * o.deposited_sign * o.better
    return df


def outcome_keys(trial: str) -> list[str]:
    return [o.key for o in TRIALS[trial].outcomes]


def outcome(trial: str, key: str) -> Outcome:
    return next(o for o in TRIALS[trial].outcomes if o.key == key)


def write_derived() -> dict:
    """Write documented CSV derivatives with every deposited column and value unchanged."""
    DERIVED_DIR.mkdir(parents=True, exist_ok=True)
    out = {}
    for k in TRIALS:
        raw, meta = load_raw(k)
        p = DERIVED_DIR / DERIVED_NAMES[k]
        raw.to_csv(p, index=False, lineterminator="\n")
        out[k] = {"path": str(p.relative_to(ROOT)), "rows": int(len(raw)), "cols": int(raw.shape[1]), "sha256": sha256sum(p)}
    return out
