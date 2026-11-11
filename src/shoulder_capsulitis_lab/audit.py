"""Data quality audit per trial. Flags are counted and reported; nothing is silently corrected."""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import data as D

BMI_TOL = 0.5          # kg/m2, deposited BMI vs weight / height^2
CHANGE_TOL = 0.011     # deposited change vs post minus pre (SPADI has two decimals)
PROTOCOL_AGE = {"spiral": (30, 60), "magneto": (35, 50)}


def change_mismatches(df: pd.DataFrame, trial: str) -> pd.DataFrame:
    rows = []
    for k in D.outcome_keys(trial):
        diff = df[f"dep_{k}"] - df[f"imp_{k}"]
        for i in np.flatnonzero(diff.abs().to_numpy() > CHANGE_TOL):
            rows.append({"trial": trial, "outcome": k, "row": int(df.row.iloc[i]), "group": int(df.group.iloc[i]),
                         "deposited_change": float(df[f"dep_{k}"].iloc[i]),
                         "recomputed_change": float(df[f"imp_{k}"].iloc[i]),
                         "deposited_minus_recomputed": float(diff.iloc[i])})
    return pd.DataFrame(rows, columns=["trial", "outcome", "row", "group", "deposited_change", "recomputed_change",
                                       "deposited_minus_recomputed"])


def repeated_spadi_pairs(df: pd.DataFrame) -> pd.DataFrame:
    """Rows whose (SPADI pre, SPADI post) pair repeats exactly in another row of the same trial."""
    key = df["pre_SPADI"].round(2).astype(str) + "|" + df["post_SPADI"].round(2).astype(str)
    dup = key.duplicated(keep=False)
    return df.loc[dup, ["row", "group", "pre_SPADI", "post_SPADI"]].assign(pair=key[dup])


def repeated_body_size(df: pd.DataFrame) -> int:
    return int(df.duplicated(["height_cm", "weight_kg"], keep=False).sum())


def audit_trial(trial: str, raw: pd.DataFrame, meta: dict, df: pd.DataFrame) -> dict:
    t = D.TRIALS[trial]
    lo, hi = PROTOCOL_AGE[trial]
    cm = change_mismatches(df, trial)
    nprs_change = df["imp_NPRS"]
    spadi_rep = repeated_spadi_pairs(df)
    facts = {
        "trial": trial,
        "file": t.file_name,
        "rows": int(len(raw)),
        "columns": int(raw.shape[1]),
        "missing_values": int(raw.isna().sum().sum()),
        "group_counts": {str(k): int(v) for k, v in df.group.value_counts().sort_index().items()},
        "sex_code_counts": {str(k): int(v) for k, v in df.sex_code.value_counts().sort_index().items()},
        "sex_by_group": {f"{g}|{s}": int(v) for (g, s), v in df.groupby(["group", "sex_code"]).size().items()},
        "age_min": float(df.age.min()), "age_max": float(df.age.max()),
        "age_under_18": int((df.age < 18).sum()),
        "protocol_age_range": [lo, hi],
        "outside_protocol_age": int(((df.age < lo) | (df.age > hi)).sum()),
        "bmi_mismatch_gt_0_5": int((df.bmi_abs_diff > BMI_TOL).sum()),
        "bmi_mismatch_max": float(df.bmi_abs_diff.max()),
        "bmi_mismatch_rows": [int(r) for r in df.loc[df.bmi_abs_diff > BMI_TOL, "row"]],
        "change_score_mismatches": int(len(cm)),
        "nprs_change_min": float(nprs_change.min()), "nprs_change_max": float(nprs_change.max()),
        "all_improved_nprs": bool((nprs_change > 0).all()),
        "all_improved_spadi": bool((df["imp_SPADI"] > 0).all()),
        "rows_improving_on_every_outcome": int(np.all([df[f"imp_{k}"] > 0 for k in D.outcome_keys(trial)], axis=0).sum()),
        "repeated_spadi_pre_post_rows": int(len(spadi_rep)),
        "repeated_spadi_pre_post_pairs": int(spadi_rep["pair"].nunique()) if len(spadi_rep) else 0,
        "repeated_height_weight_rows": repeated_body_size(df),
        "exact_duplicate_rows": int(raw.duplicated().sum()),
        "value_labels": {k: {str(kk): vv for kk, vv in v.items()} for k, v in meta.get("value_labels", {}).items()},
        "group_coding_documented": t.group_coding_documented,
    }
    if trial == "spiral":
        filt = raw["filter_$"].astype(int).to_numpy()
        facts["filter_artifact_matches_group1"] = bool((filt == (raw["GROUP"].to_numpy() == 1)).all())
        facts["diabetes_variable_present"] = False
    if trial == "magneto":
        # Sex code inference from body size only (no codebook). Reported with its uncertainty.
        hs = df.groupby("sex_code")[["height_cm", "weight_kg"]].mean()
        facts["sex_code_mean_height"] = {str(k): float(v) for k, v in hs.height_cm.items()}
        facts["sex_code_mean_weight"] = {str(k): float(v) for k, v in hs.weight_kg.items()}
    return {"facts": facts, "change_mismatches": cm, "repeated_spadi": spadi_rep}


def flag_table(audits: dict) -> pd.DataFrame:
    """One row per flag per trial. Same wording, separate trials."""
    rows = []
    s = audits["spiral"]["facts"]
    m = audits["magneto"]["facts"]
    def add(trial, fid, flag, count, detail, handling):
        rows.append({"trial": trial, "flag_id": fid, "flag": flag, "count": count, "detail": detail, "handling": handling})
    add("spiral", "S1", "Format and codebook", 1, "SPSS file only; no codebook beyond SPSS value labels (GROUP 1 EXPRIMENTAL, 2 CONTROL; GENDER 1 MALE, 2 FEMALE)",
        "Value labels used as documented; CSV derivative written")
    add("spiral", "S2", "BMI does not match height and weight (>0.5 kg/m2)", s["bmi_mismatch_gt_0_5"],
        f"max difference {s['bmi_mismatch_max']:.2f} kg/m2", "BMI recomputed for description; sensitivity without these rows")
    add("spiral", "S3", "Change score not equal to post minus pre", s["change_score_mismatches"],
        "flexion, one experimental row: deposited 66, recomputed 61 (5 degrees)", "Recomputed change used; deposited shown in sensitivity")
    add("spiral", "S4", "Uniform improvement", s["rows_improving_on_every_outcome"],
        f"every row improves on every outcome; NPRS falls by {s['nprs_change_min']:.0f} to {s['nprs_change_max']:.0f} points in all 24",
        "Regularity table and noise stress test")
    add("spiral", "S5", "SPSS filter_$ column", 1, "selects GROUP = 1; analysis artifact", "Ignored")
    add("spiral", "S6", "Protocol vs deposit", 2, "protocol: diabetic patients only and a 12 person pilot; deposit: n=24, no diabetes variable",
        "Stated; diabetes status cannot be checked")
    add("spiral", "S7", "Repeated height and weight", s["repeated_height_weight_rows"],
        "rows sharing the same height and weight with another row (148 cm, 52 kg appears 3 times)", "Reported only")
    add("magneto", "M1", "No codebook", 1, "GROUP 1/2 and GENDER 1/2 codes undocumented; generic file name NEW.xlsx",
        "Group reported as Group 1 minus Group 2; sex not used in inference")
    add("magneto", "M2", "BMI does not match height and weight (>0.5 kg/m2)", m["bmi_mismatch_gt_0_5"],
        f"max difference {m['bmi_mismatch_max']:.2f} kg/m2", "Sensitivity without these rows")
    add("magneto", "M3", "Ages outside protocol range 35 to 50", m["outside_protocol_age"],
        f"observed {m['age_min']:.0f} to {m['age_max']:.0f}", "Sensitivity restricted to 35 to 50")
    add("magneto", "M4", "Pain scale differs from protocol", 1, "protocol abstract: VAS; data: NPRS", "Analysed as NPRS, stated")
    add("magneto", "M5", "Uniform improvement", m["rows_improving_on_every_outcome"],
        f"every row improves on every outcome; NPRS falls by {m['nprs_change_min']:.0f} to {m['nprs_change_max']:.0f} points",
        "Regularity table")
    add("magneto", "M6", "Change score not equal to post minus pre", m["change_score_mismatches"], "all change scores consistent", "None needed")
    add("magneto", "M7", "Repeated SPADI pre and post pairs", m["repeated_spadi_pre_post_rows"],
        f"{m['repeated_spadi_pre_post_pairs']} identical SPADI pre/post pairs shared by {m['repeated_spadi_pre_post_rows']} rows (other columns differ)", "Sensitivity keeping first occurrence only")
    add("magneto", "M8", "Ethics and registration", 1, "not stated in deposit or abstract; not verified", "Flagged as unverified")
    return pd.DataFrame(rows)
