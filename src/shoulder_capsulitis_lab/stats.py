"""Small sample interval helpers. People are the resampling unit, always within one trial and one group."""
from __future__ import annotations

import numpy as np
from scipy import stats as st

SEED = 20261111
N_BOOT = 10000
N_PERM = 20000


def pct_ci(x, alpha=0.05):
    x = np.asarray(x, float)
    x = x[~np.isnan(x)]
    return float(np.quantile(x, alpha / 2)), float(np.quantile(x, 1 - alpha / 2))


def _boot_idx(rng, n, b=N_BOOT):
    return rng.integers(0, n, size=(b, n))


def boot_mean(x, seed=SEED, b=N_BOOT):
    x = np.asarray(x, float)
    rng = np.random.default_rng(seed)
    bm = x[_boot_idx(rng, x.size, b)].mean(axis=1)
    t = st.ttest_1samp(x, 0.0)
    ci = t.confidence_interval(0.95)
    return {"n": int(x.size), "mean": float(x.mean()), "sd": float(x.std(ddof=1)), "ci": pct_ci(bm),
            "t_ci": (float(ci.low), float(ci.high)), "min": float(x.min()), "max": float(x.max())}


def hedges_g(x1, x2):
    x1, x2 = np.asarray(x1, float), np.asarray(x2, float)
    n1, n2 = x1.size, x2.size
    sp = np.sqrt(((n1 - 1) * x1.var(ddof=1) + (n2 - 1) * x2.var(ddof=1)) / (n1 + n2 - 2))
    j = 1 - 3 / (4 * (n1 + n2) - 9)
    return float(j * (x1.mean() - x2.mean()) / sp) if sp > 0 else float("nan")


def prob_superiority(x1, x2):
    """P(random group 1 person improves more than random group 2 person), ties count one half."""
    x1, x2 = np.asarray(x1, float), np.asarray(x2, float)
    d = x1[:, None] - x2[None, :]
    return float(((d > 0).sum() + 0.5 * (d == 0).sum()) / d.size)


def hodges_lehmann(x1, x2):
    x1, x2 = np.asarray(x1, float), np.asarray(x2, float)
    return float(np.median((x1[:, None] - x2[None, :]).ravel()))


def ancova_diff(imp, pre, group1):
    """Group 1 minus group 2 difference in improvement adjusted for the baseline value (OLS)."""
    X = np.column_stack([np.ones_like(pre), group1.astype(float), pre])
    beta, *_ = np.linalg.lstsq(X, imp, rcond=None)
    return float(beta[1])


def perm_p(x1, x2, seed=SEED, n=N_PERM):
    """Two sided Monte Carlo permutation p value for the difference in means. Reported, not leaned on."""
    rng = np.random.default_rng(seed)
    x = np.concatenate([x1, x2]).astype(float)
    n1 = len(x1)
    obs = abs(np.mean(x1) - np.mean(x2))
    perms = np.argsort(rng.random((n, x.size)), axis=1)
    xs = x[perms]
    d = np.abs(xs[:, :n1].mean(axis=1) - xs[:, n1:].mean(axis=1))
    return float((1 + (d >= obs - 1e-12).sum()) / (n + 1))


def between_groups(imp1, imp2, pre1, pre2, seed=SEED, b=N_BOOT):
    """Group 1 minus group 2 contrasts in improvement, people resampled within their own group."""
    imp1, imp2 = np.asarray(imp1, float), np.asarray(imp2, float)
    pre1, pre2 = np.asarray(pre1, float), np.asarray(pre2, float)
    rng = np.random.default_rng(seed)
    i1, i2 = _boot_idx(rng, imp1.size, b), _boot_idx(rng, imp2.size, b)
    bd = imp1[i1].mean(axis=1) - imp2[i2].mean(axis=1)
    bg, banc, bps = np.empty(b), np.empty(b), np.empty(b)
    g = np.r_[np.ones(imp1.size), np.zeros(imp2.size)]
    for k in range(b):
        a, c = imp1[i1[k]], imp2[i2[k]]
        bg[k] = hedges_g(a, c)
        banc[k] = ancova_diff(np.r_[a, c], np.r_[pre1[i1[k]], pre2[i2[k]]], g)
        bps[k] = prob_superiority(a, c)
    w = st.ttest_ind(imp1, imp2, equal_var=False)
    wci = w.confidence_interval(0.95)
    return {
        "n1": int(imp1.size), "n2": int(imp2.size),
        "mean1": float(imp1.mean()), "mean2": float(imp2.mean()),
        "sd1": float(imp1.std(ddof=1)), "sd2": float(imp2.std(ddof=1)),
        "diff": float(imp1.mean() - imp2.mean()), "diff_ci": pct_ci(bd),
        "welch_ci": (float(wci.low), float(wci.high)), "welch_p": float(w.pvalue),
        "ancova": ancova_diff(np.r_[imp1, imp2], np.r_[pre1, pre2], g), "ancova_ci": pct_ci(banc),
        "hedges_g": hedges_g(imp1, imp2), "g_ci": pct_ci(bg),
        "prob_sup": prob_superiority(imp1, imp2), "ps_ci": pct_ci(bps),
        "hodges_lehmann": hodges_lehmann(imp1, imp2),
        "perm_p": perm_p(imp1, imp2, seed=seed),
    }


def noise_tolerance(imp1, imp2, sds, seed=SEED, sims=400):
    """Share of simulations where the Welch 95% CI of group 1 minus group 2 excludes zero, after adding
    independent normal noise with standard deviation `sd` to every person's improvement score."""
    rng = np.random.default_rng(seed)
    imp1, imp2 = np.asarray(imp1, float), np.asarray(imp2, float)
    out = []
    for sd in sds:
        a = imp1[None, :] + rng.normal(0, sd, (sims, imp1.size)) if sd > 0 else np.repeat(imp1[None, :], sims, 0)
        c = imp2[None, :] + rng.normal(0, sd, (sims, imp2.size)) if sd > 0 else np.repeat(imp2[None, :], sims, 0)
        m1, m2 = a.mean(1), c.mean(1)
        v1, v2 = a.var(1, ddof=1) / imp1.size, c.var(1, ddof=1) / imp2.size
        se = np.sqrt(v1 + v2)
        df = (v1 + v2) ** 2 / (v1 ** 2 / (imp1.size - 1) + v2 ** 2 / (imp2.size - 1))
        q = st.t.ppf(0.975, df)
        excl = ((m1 - m2) - q * se > 0) | ((m1 - m2) + q * se < 0)
        out.append({"added_sd": float(sd), "share_ci_excludes_zero": float(excl.mean())})
    return out
