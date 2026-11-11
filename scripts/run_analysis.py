"""Run the full Shoulder Capsulitis Lab analysis offline from the verified local deposit files.

Usage (from the project root):
    .venv/bin/python scripts/run_analysis.py

Stops with an error if either official file differs from its pinned size or sha256. Writes
data/derived/ (CSV conversions), tables/ (aggregates), figures/ (PNG and WebP),
results/summary.json and RESULTS.md. The two trials are analysed separately; nothing is pooled.
"""
from __future__ import annotations

import json
import platform
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from shoulder_capsulitis_lab import analysis as A  # noqa: E402
from shoulder_capsulitis_lab import audit as AU  # noqa: E402
from shoulder_capsulitis_lab import data as D  # noqa: E402
from shoulder_capsulitis_lab import figures as F  # noqa: E402
from shoulder_capsulitis_lab import stats as S  # noqa: E402
from shoulder_capsulitis_lab.report import write_results_md  # noqa: E402

TABLES, FIGS, RES = ROOT / "tables", ROOT / "figures", ROOT / "results"
STRESS_SDS = {"NPRS": [0, 0.5, 1, 1.5, 2, 2.5, 3], "SPADI": [0, 5, 10, 15, 20, 25, 30],
              "FLEX": [0, 5, 10, 15, 20, 25, 30], "ABD": [0, 5, 10, 15, 20, 25, 30]}


def r(x, k=4):
    if isinstance(x, (list, tuple)):
        return [r(v, k) for v in x]
    if isinstance(x, dict):
        return {str(kk): r(v, k) for kk, v in x.items()}
    if isinstance(x, (bool, np.bool_)):
        return bool(x)
    if isinstance(x, (int, np.integer)):
        return int(x)
    if isinstance(x, str) or x is None:
        return x
    return None if np.isnan(x) else round(float(x), k)


def rows_to_dict(t: pd.DataFrame) -> dict:
    keep = ["n1", "n2", "mean_improvement_group1", "mean_improvement_group2", "sd_group1", "sd_group2", "diff",
            "diff_ci_low", "diff_ci_high", "welch_ci_low", "welch_ci_high", "ancova_diff", "ancova_ci_low",
            "ancova_ci_high", "hedges_g", "g_ci_low", "g_ci_high", "prob_superiority", "ps_ci_low", "ps_ci_high",
            "hodges_lehmann", "perm_p", "welch_p"]
    return {row.outcome: {c: r(row[c]) for c in keep} for _, row in t.iterrows()}


def main():
    hashes = D.verify_raw()
    derived = D.write_derived()
    for d in (TABLES, FIGS, RES):
        d.mkdir(exist_ok=True)
        for p in d.glob("*"):
            if p.suffix in {".csv", ".png", ".webp", ".json", ".txt"}:
                p.unlink()
    frames, audits, metas = {}, {}, {}
    for k in D.TRIALS:
        raw, meta = D.load_raw(k)
        frames[k] = D.prepare(k, raw)
        audits[k] = AU.audit_trial(k, raw, meta, frames[k])
    flags = AU.flag_table(audits)
    flags.to_csv(TABLES / "t01_quality_flags.csv", index=False)
    pd.concat([audits[k]["change_mismatches"] for k in D.TRIALS]).to_csv(TABLES / "t02_change_score_mismatches.csv", index=False)
    pd.DataFrame([{"trial": k, "row": int(rw), "height_cm": frames[k].loc[frames[k].row == rw, "height_cm"].item(),
                   "weight_kg": frames[k].loc[frames[k].row == rw, "weight_kg"].item(),
                   "bmi_deposited": frames[k].loc[frames[k].row == rw, "bmi_deposited"].item(),
                   "bmi_recomputed": round(frames[k].loc[frames[k].row == rw, "bmi_recomputed"].item(), 2)}
                  for k in D.TRIALS for rw in audits[k]["facts"]["bmi_mismatch_rows"]]).to_csv(TABLES / "t03_bmi_mismatches.csv", index=False)

    out = {"meta": {"python": platform.python_version(), "pandas": pd.__version__, "numpy": np.__version__,
                    "seed": S.SEED, "n_boot": S.N_BOOT, "n_perm": S.N_PERM, "pooled": False,
                    "note": "Two separate trials. No rows were combined and no combined treatment effect was computed."},
           "hashes": hashes, "derived": derived, "trials": {}}
    base, within, prim, sens, reg, nprs = [], [], [], [], [], {}
    for k, df in frames.items():
        b = A.baseline_table(df)
        w = A.within_group(df)
        p = A.contrasts(df)
        rep_rows = [int(x) for x in audits[k]["repeated_spadi"]["row"]] if len(audits[k]["repeated_spadi"]) else []
        s = A.sensitivity(df, k, rep_rows)
        g = A.regularity(df)
        nprs[k] = A.nprs_distribution(df)
        base.append(b); within.append(w); prim.append(p); sens.append(s); reg.append(g)
        t = D.TRIALS[k]
        facts = dict(audits[k]["facts"])
        out["trials"][k] = {
            "title": t.title, "doi": t.doi, "concept_doi": t.concept_doi, "url": t.url, "published": t.published,
            "file": t.file_name, "sha256": t.sha256, "size": t.size, "intervention": t.intervention, "dose": t.dose,
            "group_labels": {str(a): v for a, v in t.group_labels.items()},
            "audit": r(facts),
            "within_group": {f"{row.outcome}|{row.group}": {"mean": r(row.improvement_mean), "sd": r(row.improvement_sd),
                                                             "ci": r([row.boot_ci_low, row.boot_ci_high]),
                                                             "pre": r(row.pre_mean), "post": r(row.post_mean)}
                             for _, row in w.iterrows()},
            "primary": rows_to_dict(p),
            "sensitivity": {a: rows_to_dict(s[s.analysis == a]) for a in dict.fromkeys(s.analysis)},
            "regularity": {f"{row.outcome}|{row.group}": {c: r(row[c]) for c in ["sd_baseline", "sd_post", "min_post", "max_post", "sd_improvement",
                           "ratio_sd_improvement_to_baseline", "min_improvement", "max_improvement",
                           "distinct_improvement_values", "corr_pre_post"]}
                           for _, row in g[g.group.isin([1, 2])].iterrows()},
            "groups_fully_separated": {row.outcome: bool(row.groups_fully_separated) for _, row in g[g.group == "overlap"].iterrows()},
            "post_values_fully_separated": {row.outcome: bool(row.post_values_fully_separated) for _, row in g[g.group == "overlap"].iterrows()},
            "nprs_drop_distribution": {f"{int(row.group)}|{int(row.nprs_drop_points)}": int(row.n) for _, row in nprs[k].iterrows()},
        }
    # Tables are stacked one trial after another for convenience; every row carries its trial and
    # nothing is computed across trials.
    pd.concat(base).to_csv(TABLES / "t04_baseline_by_group.csv", index=False, float_format="%.3f")
    pd.concat(within).to_csv(TABLES / "t05_within_group_change.csv", index=False, float_format="%.3f")
    pd.concat(prim).to_csv(TABLES / "t06_between_group_primary.csv", index=False, float_format="%.4f")
    pd.concat(sens).to_csv(TABLES / "t07_sensitivity.csv", index=False, float_format="%.4f")
    pd.concat(reg).to_csv(TABLES / "t08_regularity.csv", index=False, float_format="%.4f")
    pd.concat(nprs.values()).to_csv(TABLES / "t09_nprs_drop_distribution.csv", index=False)
    stress = A.stress_test(frames["spiral"], STRESS_SDS)
    stress.to_csv(TABLES / "t10_spiral_noise_stress.csv", index=False, float_format="%.4f")
    out["stress_spiral"] = {f"{row.outcome}|{row.added_sd:g}": r(row.share_ci_excludes_zero) for _, row in stress.iterrows()}
    side = pd.concat(prim)[["trial", "outcome", "label", "hedges_g", "g_ci_low", "g_ci_high", "diff", "diff_ci_low", "diff_ci_high"]]
    side.to_csv(TABLES / "t11_side_by_side_no_pooling.csv", index=False, float_format="%.4f")

    figs = []
    figs += F.fig_flags(flags, FIGS / "fig01_quality_flags.png")
    figs += F.fig_design(FIGS / "fig02_two_separate_trials.png")
    figs += F.fig_prepost(frames["spiral"], "spiral", FIGS / "fig03_spiral_before_after.png", "fig03")
    figs += F.fig_prepost(frames["magneto"], "magneto", FIGS / "fig04_magneto_before_after.png", "fig04")
    figs += F.fig_contrasts(pd.concat(prim), FIGS / "fig05_between_group_side_by_side.png")
    figs += F.fig_regularity(nprs, {k: g for k, g in zip(frames, reg)}, FIGS / "fig06_regularity.png")
    figs += F.fig_sensitivity(pd.concat(sens), FIGS / "fig07_sensitivity.png")
    figs += F.fig_stress(stress, FIGS / "fig08_spiral_noise_stress.png")
    out["figures"] = sorted(p.name for p in figs)
    out["tables"] = sorted(p.name for p in TABLES.glob("*.csv"))
    (RES / "summary.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    log = [f"python {platform.python_version()} pandas {pd.__version__} numpy {np.__version__}"]
    log += [f"verified {n} sha256 {h}" for n, h in hashes.items()]
    log += [f"derived {v['path']} rows {v['rows']} cols {v['cols']}" for v in derived.values()]
    log += [f"tables {len(out['tables'])}", f"figures {len(out['figures'])}", "pooled False"]
    (RES / "run_log.txt").write_text("\n".join(log) + "\n", encoding="utf-8")
    write_results_md(out, ROOT / "RESULTS.md")
    print("\n".join(log))


if __name__ == "__main__":
    main()
