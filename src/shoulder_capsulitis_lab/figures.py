"""Figures (PNG with WebP twins). Original drawings from the deposited files only; nothing from the JCDR protocols.

Each trial is drawn in its own panel. No figure shows a pooled estimate.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from PIL import Image  # noqa: E402

from . import data as D  # noqa: E402

FOOTER = ("Data: Krishnagopal Mondal and Sunita Sharma 2025, Mendeley Data doi 10.17632/hnvhm376hg.1; Kumar and Pattnaik 2026, Mendeley Data "
          "doi 10.17632/khdtg3rzmp.1; both CC BY 4.0. Analysis: Shoulder Capsulitis Lab. Two separate small trials, never pooled.")
COL = {1: "#c8553d", 2: "#3b75af"}
TRIAL_COL = {"spiral": "#7a4fa0", "magneto": "#2f8f6f"}
TITLES = {
    "fig01": "Data audit: quality flags per deposit",
    "fig02": "Two separate deposits, two separate analyses",
    "fig03": "Spiral Stretch trial: every person, before and after",
    "fig04": "Magnetotherapy trial: every person, before and after",
    "fig05": "Between group contrasts, each trial on its own (Hedges g, 95% bootstrap CI)",
    "fig06": "How regular are the changes?",
    "fig07": "Sensitivity analyses for the known data problems",
    "fig08": "Stress test: how much extra noise before the Spiral Stretch contrast disappears?",
}
plt.rcParams.update({"axes.unicode_minus": False, "font.size": 10, "axes.spines.top": False, "axes.spines.right": False})


def _save(fig, path: Path, caption: str) -> list[Path]:
    fig.text(0.01, 0.01, caption + "\n" + FOOTER, fontsize=7.2, color="#444", va="bottom", wrap=True)
    fig.savefig(path, dpi=150)
    plt.close(fig)
    webp = path.with_suffix(".webp")
    Image.open(path).save(webp, "WEBP", quality=90, method=6)
    return [path, webp]


def fig_flags(flags: pd.DataFrame, path: Path):
    fig, axs = plt.subplots(1, 2, figsize=(13, 5.6))
    fig.subplots_adjust(left=0.27, bottom=0.2, top=0.86, wspace=1.05, right=0.97)
    fig.suptitle(TITLES["fig01"], x=0.01, ha="left", fontsize=12)
    for ax, trial in zip(axs, ["spiral", "magneto"]):
        f = flags[flags.trial == trial].iloc[::-1]
        ax.barh(np.arange(len(f)), f["count"], color=TRIAL_COL[trial])
        ax.set_yticks(np.arange(len(f)), [f"{a}  {b}" for a, b in zip(f.flag_id, f.flag)], fontsize=8)
        for i, v in enumerate(f["count"]):
            ax.text(v + 0.3, i, str(v), va="center", fontsize=8)
        ax.set_xlabel("rows or items affected")
        ax.set_title(f"{D.TRIALS[trial].short}, n={D.TRIALS[trial].n_expected}", loc="left", fontsize=10)
    return _save(fig, path, "Counts from the deposited files. Flags are reported, not corrected; see RESULTS.md for handling.")


def fig_design(path: Path):
    fig, ax = plt.subplots(figsize=(12, 5.2))
    fig.subplots_adjust(bottom=0.16, top=0.88)
    fig.suptitle(TITLES["fig02"], x=0.01, ha="left", fontsize=12)
    ax.axis("off")
    boxes = [
        (0.02, "spiral", ["Mendeley hnvhm376hg V1 (27 Mar 2025)", "Spiral Stretch + PT vs PT alone",
                          "4 weeks, 3 sessions per week (protocol)", "n=24 (12 and 12), ages 30 to 60",
                          "SPADI, NPRS, 5 ROM directions", "SPSS file, value labels only",
                          "Protocol: diabetic patients, 12 person pilot", "No results paper"]),
        (0.53, "magneto", ["Mendeley khdtg3rzmp V1 (29 May 2026)", "Magnetotherapy + PT vs PT (coding undocumented)",
                           "2 weeks, 2 sessions per week (abstract)", "n=36 (18 and 18), ages 32 to 60",
                           "SPADI, NPRS, 6 ROM directions (adds adduction)", "Excel file, no codebook",
                           "Abstract: ages 35 to 50, VAS for pain", "No results paper"]),
    ]
    for x0, trial, lines in boxes:
        ax.add_patch(plt.Rectangle((x0, 0.08), 0.45, 0.82, fill=False, lw=2, ec=TRIAL_COL[trial], transform=ax.transAxes))
        ax.text(x0 + 0.02, 0.83, D.TRIALS[trial].short, fontsize=12, weight="bold", color=TRIAL_COL[trial], transform=ax.transAxes)
        for i, l in enumerate(lines):
            ax.text(x0 + 0.02, 0.74 - i * 0.083, l, fontsize=9.5, transform=ax.transAxes)
    ax.text(0.5, 0.49, "not\npooled", ha="center", va="center", fontsize=10, color="#a00", weight="bold", transform=ax.transAxes)
    return _save(fig, path, "Same centre (MM, Mullana, India), different interventions, doses, variable names and ROM sets. "
                            "No rows are combined and no combined treatment effect is computed.")


def fig_prepost(df: pd.DataFrame, trial: str, path: Path, fid: str):
    keys = ["SPADI", "NPRS", "FLEX", "ABD"]
    fig, axs = plt.subplots(1, 4, figsize=(13, 4.8))
    fig.subplots_adjust(bottom=0.25, top=0.8, wspace=0.35)
    fig.suptitle(TITLES[fid], x=0.01, ha="left", fontsize=12)
    t = D.TRIALS[trial]
    for ax, k in zip(axs, keys):
        o = D.outcome(trial, k)
        for g, off in ((1, -0.08), (2, 0.08)):
            s = df[df.group == g]
            for _, r in s.iterrows():
                ax.plot([0 + off, 1 + off], [r[f"pre_{k}"], r[f"post_{k}"]], color=COL[g], alpha=0.35, lw=1)
            ax.plot([0 + off, 1 + off], [s[f"pre_{k}"].mean(), s[f"post_{k}"].mean()], color=COL[g], lw=3,
                    label=t.group_labels[g])
        ax.set_xticks([0, 1], ["before", "after"])
        ax.set_xlim(-0.4, 1.4)
        ax.set_title(o.label, fontsize=9.5)
        ax.set_ylabel(o.unit)
    axs[0].legend(frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(2.4, 1.2), ncol=2)
    cap = ("Thin lines: one person. Thick lines: group mean. Lower is better for SPADI and NPRS; higher is better for ROM.")
    if trial == "magneto":
        cap += " Group codes are not documented in the deposit."
    return _save(fig, path, cap)


def fig_contrasts(primary: pd.DataFrame, path: Path):
    fig, axs = plt.subplots(1, 2, figsize=(12, 5.2), sharex=True)
    fig.subplots_adjust(left=0.14, bottom=0.22, top=0.84, wspace=0.45)
    fig.suptitle(TITLES["fig05"], x=0.01, ha="left", fontsize=12)
    for ax, trial in zip(axs, ["spiral", "magneto"]):
        p = primary[primary.trial == trial].iloc[::-1].reset_index(drop=True)
        y = np.arange(len(p))
        ax.errorbar(p.hedges_g, y, xerr=[p.hedges_g - p.g_ci_low, p.g_ci_high - p.hedges_g], fmt="o",
                    color=TRIAL_COL[trial], capsize=3)
        ax.axvline(0, color="#888", lw=1)
        ax.set_yticks(y, p.label, fontsize=8.5)
        ax.set_title(D.TRIALS[trial].short + (" (Group 1 minus Group 2)" if trial == "magneto" else " (Spiral minus control)"),
                     loc="left", fontsize=9.5)
        ax.set_xlabel("standardised difference in improvement (positive favours group 1)")
    return _save(fig, path, "Each panel is its own trial. There is deliberately no pooled or combined estimate. "
                            "The very large Spiral Stretch values reflect very small spread in the change scores (see fig06).")


def fig_regularity(nprs: dict, reg: dict, path: Path):
    fig, axs = plt.subplots(1, 2, figsize=(12.5, 5.2))
    fig.subplots_adjust(bottom=0.24, top=0.84, wspace=0.3)
    fig.suptitle(TITLES["fig06"], x=0.01, ha="left", fontsize=12)
    ax = axs[0]
    vals = np.arange(0, 7)
    width = 0.2
    i = 0
    for trial in ["spiral", "magneto"]:
        d = nprs[trial]
        for g in (1, 2):
            cnt = [int(d[(d.group == g) & (d.nprs_drop_points == v)]["n"].sum()) for v in vals]
            ax.bar(vals + (i - 1.5) * width, cnt, width, color=TRIAL_COL[trial], alpha=1.0 if g == 1 else 0.45,
                   label=f"{D.TRIALS[trial].short}, group {g}")
            i += 1
    ax.set_xlabel("pain drop on NPRS, points (before minus after)")
    ax.set_ylabel("people")
    ax.set_title("Nobody's pain dropped by fewer than 2 or more than 5 points", loc="left", fontsize=9.5)
    ax.legend(frameon=False, fontsize=7.5)
    ax = axs[1]
    for trial, mk in (("spiral", "o"), ("magneto", "s")):
        r = reg[trial]
        r = r[r.group.isin([1, 2])]
        for g in (1, 2):
            s = r[r.group == g]
            ax.scatter(s.outcome, s.ratio_sd_improvement_to_baseline, marker=mk, color=TRIAL_COL[trial],
                       alpha=1.0 if g == 1 else 0.45, label=f"{D.TRIALS[trial].short}, group {g}")
    ax.axhline(1, color="#888", ls=":", lw=1)
    ax.set_ylabel("SD of change / SD at baseline")
    ax.set_title("Spread of change relative to spread at baseline", loc="left", fontsize=9.5)
    ax.legend(frameon=False, fontsize=7.5)
    return _save(fig, path, "Every person in both deposits improved on every outcome. Patterns are compared side by side, "
                            "not combined.")


def fig_sensitivity(sens: pd.DataFrame, path: Path):
    keys = ["SPADI", "NPRS", "FLEX"]
    fig, axs = plt.subplots(1, 2, figsize=(13, 5.6))
    fig.subplots_adjust(left=0.2, bottom=0.2, top=0.85, wspace=0.75)
    fig.suptitle(TITLES["fig07"], x=0.01, ha="left", fontsize=12)
    for ax, trial in zip(axs, ["spiral", "magneto"]):
        s = sens[(sens.trial == trial) & sens.outcome.isin(keys)]
        labels = list(dict.fromkeys(s.analysis))
        y = 0
        ticks, tl = [], []
        for k in keys:
            for j, a in enumerate(labels):
                r = s[(s.outcome == k) & (s.analysis == a)].iloc[0]
                ax.errorbar(r.hedges_g, y, xerr=[[r.hedges_g - r.g_ci_low], [r.g_ci_high - r.hedges_g]], fmt="o",
                            color=TRIAL_COL[trial], alpha=1 - 0.2 * j, capsize=2)
                ticks.append(y)
                tl.append(f"{k} · {a.split(':')[0]} (n={int(r.n1)}+{int(r.n2)})")
                y -= 1
            y -= 0.6
        ax.set_yticks(ticks, tl, fontsize=7.5)
        ax.axvline(0, color="#888", lw=1)
        ax.set_xlabel("Hedges g, 95% bootstrap CI")
        ax.set_title(D.TRIALS[trial].short, loc="left", fontsize=10)
    return _save(fig, path, "P primary. Spiral: S1 rows with consistent BMI only, S2 deposited change scores. "
                            "Magnetotherapy: S1 consistent BMI only, S2 protocol ages 35 to 50, S3 repeated SPADI pairs once.")


def fig_stress(stress: pd.DataFrame, path: Path):
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.8))
    fig.subplots_adjust(bottom=0.25, top=0.84, wspace=0.3)
    fig.suptitle(TITLES["fig08"], x=0.01, ha="left", fontsize=12)
    for ax, keys, unit in ((axs[0], ["NPRS"], "NPRS points"), (axs[1], ["SPADI", "FLEX", "ABD"], "SPADI points or degrees")):
        for k in keys:
            s = stress[stress.outcome == k]
            ax.plot(s.added_sd, s.share_ci_excludes_zero, marker="o", label=k)
        ax.axhline(0.5, color="#888", ls=":", lw=1)
        ax.set_xlabel(f"SD of the added noise ({unit})")
        ax.set_ylabel("share of simulations with 95% CI excluding 0")
        ax.set_ylim(-0.02, 1.02)
        ax.legend(frameon=False, fontsize=8)
    return _save(fig, path, "Spiral Stretch trial only. 400 simulations per noise level, Welch interval. "
                            "This asks how fragile the contrast is if the true measurement noise were larger than recorded.")
