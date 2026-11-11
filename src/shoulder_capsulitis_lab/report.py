"""Writes RESULTS.md from results/summary.json values. Each trial gets its own section."""
from __future__ import annotations

from pathlib import Path

from . import data as D


def f(x, k=1):
    return "n/a" if x is None else f"{x:.{k}f}"


def s(x, k=1):
    return "n/a" if x is None else (f"+{x:.{k}f}" if x > 0 else f"{x:.{k}f}")


def ci(lo, hi, k=1, signed=True):
    fn = s if signed else f
    return f"{fn(lo, k)} to {fn(hi, k)}"


def pf(p):
    return "<0.001" if p < 0.001 else f"{p:.3f}"


def dec(o):
    return 2 if o in ("NPRS",) else 1


def trial_section(key: str, t: dict) -> list[str]:
    tr = D.TRIALS[key]
    a = t["audit"]
    L = [f"## {tr.short} ({tr.doi})", ""]
    L += [f"Intervention: {tr.intervention}. Dose: {tr.dose}. n={a['rows']} "
          f"({a['group_counts']['1']} and {a['group_counts']['2']}), ages {a['age_min']:.0f} to {a['age_max']:.0f}.", ""]
    if key == "magneto":
        L += ["Group 1 and Group 2 are reported as coded. The deposit does not say which code is magnetotherapy. "
              "By analogy with the Spiral Stretch file from the same department (1 = experimental) and the order in the "
              "abstract, Group 1 is presumed to be magnetotherapy plus physiotherapy. This is an inference, not a fact. "
              "Because no contrast differs from zero, the direction does not change the conclusion.", ""]
    L += ["### Change within each group (improvement, positive = better; mean, 95% bootstrap CI)", "",
          f"| Outcome | {tr.group_labels[1]} before → after | improvement | {tr.group_labels[2]} before → after | improvement |",
          "|-|-|-|-|-|"]
    for o in tr.outcomes:
        w1, w2 = t["within_group"][f"{o.key}|1"], t["within_group"][f"{o.key}|2"]
        k = dec(o.key)
        L.append(f"| {o.label} | {f(w1['pre'])} → {f(w1['post'])} | {f(w1['mean'], k)} ({ci(*w1['ci'], k, False)}) | "
                 f"{f(w2['pre'])} → {f(w2['post'])} | {f(w2['mean'], k)} ({ci(*w2['ci'], k, False)}) |")
    L += ["", "### Between groups (group 1 minus group 2 improvement)", "",
          "| Outcome | Difference (95% bootstrap CI) | Welch 95% CI | Baseline adjusted (95% CI) | Hedges g (95% CI) | P(superiority) | Permutation p |",
          "|-|-|-|-|-|-|-|"]
    for o in tr.outcomes:
        p = t["primary"][o.key]
        k = dec(o.key)
        L.append(f"| {o.label} | {s(p['diff'], k)} ({ci(p['diff_ci_low'], p['diff_ci_high'], k)}) | "
                 f"{ci(p['welch_ci_low'], p['welch_ci_high'], k)} | {s(p['ancova_diff'], k)} ({ci(p['ancova_ci_low'], p['ancova_ci_high'], k)}) | "
                 f"{s(p['hedges_g'], 2)} ({ci(p['g_ci_low'], p['g_ci_high'], 2)}) | {f(p['prob_superiority'], 2)} | {pf(p['perm_p'])} |")
    L += ["", "### Sensitivity analyses (difference in improvement, 95% bootstrap CI)", "",
          "| Analysis | n | SPADI | NPRS | Flexion |", "|-|-|-|-|-|"]
    for name, rows in t["sensitivity"].items():
        sp, np_, fl = rows["SPADI"], rows["NPRS"], rows["FLEX"]
        L.append(f"| {name} | {sp['n1']} + {sp['n2']} | {s(sp['diff'])} ({ci(sp['diff_ci_low'], sp['diff_ci_high'])}) | "
                 f"{s(np_['diff'], 2)} ({ci(np_['diff_ci_low'], np_['diff_ci_high'], 2)}) | "
                 f"{s(fl['diff'])} ({ci(fl['diff_ci_low'], fl['diff_ci_high'])}) |")
    flips = [(name, k, v) for name, rows in t["sensitivity"].items() if not name.startswith("P:")
             for k, v in rows.items() if (v["diff_ci_low"] > 0 or v["diff_ci_high"] < 0) != (t["primary"][k]["diff_ci_low"] > 0 or t["primary"][k]["diff_ci_high"] < 0)]
    n_sens = sum(len(rows) for name, rows in t["sensitivity"].items() if not name.startswith("P:"))
    L += ["", f"Sensitivity contrasts (all outcomes) whose conclusion differs from the primary analysis: {len(flips)} of {n_sens}."]
    for name, k, v in flips:
        L.append(f"* {name}, {k}: {s(v['diff'], 1)} ({ci(v['diff_ci_low'], v['diff_ci_high'], 1)}), n={v['n1']} + {v['n2']}. "
                 "Interval excludes zero here but not in the primary analysis; with this many looks one such result is expected by chance.")
    sep = [k for k, v in t["groups_fully_separated"].items() if v]
    psep = [k for k, v in t["post_values_fully_separated"].items() if v]
    dist = t["nprs_drop_distribution"]
    L += ["", "### Regularity", "",
          f"* Every one of the {a['rows']} people improved on every outcome ({a['rows_improving_on_every_outcome']} of {a['rows']}).",
          f"* Pain dropped by {a['nprs_change_min']:.0f} to {a['nprs_change_max']:.0f} NPRS points in every person. "
          "Counts (group|points: people): " + ", ".join(f"{k}: {v}" for k, v in dist.items()) + ".",
          f"* Outcomes where the two groups' improvement ranges do not overlap at all: {', '.join(sep) if sep else 'none'}.",
          f"* Outcomes where the two groups' values after treatment do not overlap at all: {', '.join(psep) if psep else 'none'}.",
          "* SD of improvement divided by SD at baseline, group 1 / group 2: " + ", ".join(
              f"{o.key} {f(t['regularity'][o.key + '|1']['ratio_sd_improvement_to_baseline'], 2)} / "
              f"{f(t['regularity'][o.key + '|2']['ratio_sd_improvement_to_baseline'], 2)}" for o in tr.outcomes) + ".",
          "* Range of values after treatment, group 1 / group 2: " + ", ".join(
              f"{o.key} {f(t['regularity'][o.key + '|1']['min_post'], 0 if o.unit == 'degrees' else 1)} to "
              f"{f(t['regularity'][o.key + '|1']['max_post'], 0 if o.unit == 'degrees' else 1)} / "
              f"{f(t['regularity'][o.key + '|2']['min_post'], 0 if o.unit == 'degrees' else 1)} to "
              f"{f(t['regularity'][o.key + '|2']['max_post'], 0 if o.unit == 'degrees' else 1)}" for o in tr.outcomes) + ".", ""]
    return L


def write_results_md(out: dict, path: Path):
    sp, mg = out["trials"]["spiral"], out["trials"]["magneto"]
    st = out["stress_spiral"]
    L = ["# Results", "",
         "Generated by `scripts/run_analysis.py` from the two verified deposit files. Numbers here are copied from "
         "`results/summary.json`. Do not edit by hand.", "",
         "**The two trials are analysed separately. No rows are pooled and no combined treatment effect is reported.** "
         "Neither trial has a published results paper; only a protocol (Spiral Stretch) and a protocol abstract "
         "(magnetotherapy) exist. Nothing here replicates or checks a published result.", "",
         f"Methods in brief: improvement is post minus pre for ROM and pre minus post for SPADI and NPRS, recomputed from "
         f"the deposited pre and post values. Intervals are 95% percentile bootstrap intervals with people resampled within "
         f"their own group ({out['meta']['n_boot']} resamples, seed {out['meta']['seed']}). Welch intervals, a baseline "
         f"adjusted difference (ANCOVA), Hedges g, the probability of superiority and a Monte Carlo permutation p value "
         f"({out['meta']['n_perm']} permutations) are given as context. With 12 or 18 people per group, p values are "
         "fragile and are not the basis of any conclusion.", ""]
    L += ["## Integrity", "", "| File | sha256 |", "|-|-|"]
    L += [f"| `{n}` | `{h}` |" for n, h in out["hashes"].items()]
    L += [""]
    L += trial_section("spiral", sp)
    L += ["### Noise stress test (Spiral Stretch only)", "",
          "Independent normal noise was added to every person's improvement score, 400 simulations per level. "
          "Share of simulations whose Welch 95% CI still excludes zero:", "",
          "| Added SD | NPRS | Added SD | SPADI | Flexion | Abduction |", "|-|-|-|-|-|-|"]
    for a, b in zip([0, 0.5, 1, 1.5, 2, 2.5, 3], [0, 5, 10, 15, 20, 25, 30]):
        L.append(f"| {a:g} points | {f(st[f'NPRS|{a:g}'], 2)} | {b} | {f(st[f'SPADI|{b}'], 2)} | {f(st[f'FLEX|{b}'], 2)} | {f(st[f'ABD|{b}'], 2)} |")
    L += [""]
    L += trial_section("magneto", mg)
    L += ["## Side by side, not pooled", "",
          "Table `tables/t11_side_by_side_no_pooling.csv` lists each trial's Hedges g next to the other. It has no "
          "combined row by design. The pattern: the Spiral Stretch deposit shows large, consistent between group "
          "differences on every outcome; the magnetotherapy deposit shows near identical improvement in both groups on "
          "every outcome. Both deposits share an unusual feature: every participant improved on every outcome.", "",
          "## Files", "", "Tables: " + ", ".join(f"`{t}`" for t in out["tables"]) + ".", "",
          "Figures: " + ", ".join(f"`{x}`" for x in out["figures"] if x.endswith(".png")) + " (each with a WebP twin).", ""]
    path.write_text("\n".join(L), encoding="utf-8")
