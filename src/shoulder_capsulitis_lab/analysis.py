"""Per trial analyses. Every function takes ONE trial frame; no function combines trials."""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import data as D
from . import stats as S


def assert_single_trial(df: pd.DataFrame) -> str:
    trials = df["trial"].unique()
    if len(trials) != 1:
        raise ValueError(f"refusing to analyse rows from more than one trial together: {sorted(trials)}")
    return str(trials[0])


def baseline_table(df: pd.DataFrame) -> pd.DataFrame:
    trial = assert_single_trial(df)
    rows = []
    cols = [("age", "Age, years"), ("height_cm", "Height, cm"), ("weight_kg", "Weight, kg"),
            ("bmi_deposited", "BMI as deposited"), ("bmi_recomputed", "BMI recomputed")]
    cols += [(f"pre_{o.key}", f"Baseline {o.label}") for o in D.TRIALS[trial].outcomes]
    for c, lab in cols:
        r = {"trial": trial, "variable": lab}
        for g in (1, 2):
            x = df.loc[df.group == g, c]
            r[f"group{g}_mean"] = x.mean()
            r[f"group{g}_sd"] = x.std(ddof=1)
        r["group1_minus_group2"] = r["group1_mean"] - r["group2_mean"]
        rows.append(r)
    return pd.DataFrame(rows)


def within_group(df: pd.DataFrame) -> pd.DataFrame:
    trial = assert_single_trial(df)
    rows = []
    for o in D.TRIALS[trial].outcomes:
        for g in (1, 2):
            sub = df[df.group == g]
            r = S.boot_mean(sub[f"imp_{o.key}"].to_numpy(), seed=S.SEED + g)
            rows.append({"trial": trial, "outcome": o.key, "label": o.label, "unit": o.unit, "group": g,
                         "group_label": D.TRIALS[trial].group_labels[g], "n": r["n"],
                         "pre_mean": sub[f"pre_{o.key}"].mean(), "post_mean": sub[f"post_{o.key}"].mean(),
                         "improvement_mean": r["mean"], "improvement_sd": r["sd"],
                         "boot_ci_low": r["ci"][0], "boot_ci_high": r["ci"][1],
                         "t_ci_low": r["t_ci"][0], "t_ci_high": r["t_ci"][1],
                         "min_improvement": r["min"], "max_improvement": r["max"],
                         "share_improved": float((sub[f"imp_{o.key}"] > 0).mean())})
    return pd.DataFrame(rows)


def contrasts(df: pd.DataFrame, which: str = "imp", label: str = "primary") -> pd.DataFrame:
    trial = assert_single_trial(df)
    rows = []
    for o in D.TRIALS[trial].outcomes:
        a, c = df[df.group == 1], df[df.group == 2]
        r = S.between_groups(a[f"{which}_{o.key}"], c[f"{which}_{o.key}"], a[f"pre_{o.key}"], c[f"pre_{o.key}"])
        rows.append({"trial": trial, "analysis": label, "outcome": o.key, "label": o.label, "unit": o.unit,
                     "n1": r["n1"], "n2": r["n2"],
                     "mean_improvement_group1": r["mean1"], "mean_improvement_group2": r["mean2"],
                     "sd_group1": r["sd1"], "sd_group2": r["sd2"],
                     "diff": r["diff"], "diff_ci_low": r["diff_ci"][0], "diff_ci_high": r["diff_ci"][1],
                     "welch_ci_low": r["welch_ci"][0], "welch_ci_high": r["welch_ci"][1],
                     "ancova_diff": r["ancova"], "ancova_ci_low": r["ancova_ci"][0], "ancova_ci_high": r["ancova_ci"][1],
                     "hedges_g": r["hedges_g"], "g_ci_low": r["g_ci"][0], "g_ci_high": r["g_ci"][1],
                     "prob_superiority": r["prob_sup"], "ps_ci_low": r["ps_ci"][0], "ps_ci_high": r["ps_ci"][1],
                     "hodges_lehmann": r["hodges_lehmann"], "perm_p": r["perm_p"], "welch_p": r["welch_p"]})
    return pd.DataFrame(rows)


def regularity(df: pd.DataFrame) -> pd.DataFrame:
    """How regular are the changes? Spread of change vs spread at baseline, distinct values, overlap."""
    trial = assert_single_trial(df)
    rows = []
    for o in D.TRIALS[trial].outcomes:
        for g in (1, 2):
            s = df[df.group == g]
            imp, pre, post = s[f"imp_{o.key}"], s[f"pre_{o.key}"], s[f"post_{o.key}"]
            rows.append({"trial": trial, "outcome": o.key, "group": g, "n": int(len(s)),
                         "sd_baseline": pre.std(ddof=1), "sd_post": post.std(ddof=1), "sd_improvement": imp.std(ddof=1),
                         "min_post": post.min(), "max_post": post.max(),
                         "ratio_sd_improvement_to_baseline": imp.std(ddof=1) / pre.std(ddof=1),
                         "min_improvement": imp.min(), "max_improvement": imp.max(),
                         "distinct_improvement_values": int(imp.nunique()),
                         "corr_pre_post": float(np.corrcoef(pre, post)[0, 1]),
                         "share_improved": float((imp > 0).mean())})
        a, c = df.loc[df.group == 1, f"imp_{o.key}"], df.loc[df.group == 2, f"imp_{o.key}"]
        pa, pc = df.loc[df.group == 1, f"post_{o.key}"], df.loc[df.group == 2, f"post_{o.key}"]
        rows.append({"trial": trial, "outcome": o.key, "group": "overlap",
                     "n": int(len(df)), "group1_min": a.min(), "group2_max": c.max(),
                     "groups_fully_separated": bool(a.min() > c.max() or c.min() > a.max()),
                     "post_values_fully_separated": bool(pa.min() > pc.max() or pc.min() > pa.max()
                                                         or pa.max() < pc.min() or pc.max() < pa.min())})
    return pd.DataFrame(rows)


def nprs_distribution(df: pd.DataFrame) -> pd.DataFrame:
    trial = assert_single_trial(df)
    t = df.groupby(["group", "imp_NPRS"]).size().rename("n").reset_index()
    t.insert(0, "trial", trial)
    return t.rename(columns={"imp_NPRS": "nprs_drop_points"})


def stress_test(df: pd.DataFrame, sds_by_outcome: dict) -> pd.DataFrame:
    trial = assert_single_trial(df)
    rows = []
    for k, sds in sds_by_outcome.items():
        a, c = df.loc[df.group == 1, f"imp_{k}"], df.loc[df.group == 2, f"imp_{k}"]
        for r in S.noise_tolerance(a, c, sds):
            rows.append({"trial": trial, "outcome": k, **r})
    return pd.DataFrame(rows)


def sensitivity(df: pd.DataFrame, trial: str, repeated_spadi_rows: list[int]) -> pd.DataFrame:
    """Re-run the primary contrasts on the documented problem subsets. Each trial on its own."""
    assert assert_single_trial(df) == trial
    out = [contrasts(df, "imp", "P: primary (recomputed change)")]
    out.append(contrasts(df[df.bmi_abs_diff <= 0.5], "imp", "S1: drop rows with BMI mismatch"))
    if trial == "spiral":
        out.append(contrasts(df, "dep", "S2: deposited change scores (flexion error kept)"))
    else:
        out.append(contrasts(df[(df.age >= 35) & (df.age <= 50)], "imp", "S2: protocol ages 35 to 50 only"))
        keep = ~df.duplicated(["pre_SPADI", "post_SPADI"], keep="first")
        out.append(contrasts(df[keep], "imp", "S3: repeated SPADI pairs, first occurrence only"))
    return pd.concat(out, ignore_index=True)
