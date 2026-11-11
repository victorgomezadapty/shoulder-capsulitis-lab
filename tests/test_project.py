"""Integrity, no pooling, audit, numeric lock, license and wording tests for Shoulder Capsulitis Lab."""
import ast
import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from shoulder_capsulitis_lab import analysis as A  # noqa: E402
from shoulder_capsulitis_lab import audit as AU  # noqa: E402
from shoulder_capsulitis_lab import data as D  # noqa: E402

DOCS = ["README.md", "RESULTS.md", "DATA_LICENSE.md", "PROVENANCE.md", "ANALYSIS_PLAN.md", "DISCUSSION.md",
        "PORTFOLIO_BRIEF.md", "LICENSE", "data/derived/README.md"]
FORBIDDEN_DASHES = ["\u2010", "\u2011", "\u2012", "\u2013", "\u2014", "\u2015", "\u2212", "--"]
FORBIDDEN_NAMES = ["optimo", "malqa", "riyadh"]
SPIRAL_SHA = "61f73cffa6a301cd29097a5adc21c48cadcc563f484cfd92eaa58b2e51be0e3d"
MAGNETO_SHA = "18c9ee575c8babd2f1da4d137fb970f82e04d53c6158dd914c93776069e10b56"


@pytest.fixture(scope="module")
def frames():
    out = {}
    for k in D.TRIALS:
        raw, meta = D.load_raw(k)
        out[k] = (raw, meta, D.prepare(k, raw))
    return out


@pytest.fixture(scope="module")
def audits(frames):
    return {k: AU.audit_trial(k, *v) for k, v in frames.items()}


@pytest.fixture(scope="module")
def summary():
    return json.loads((ROOT / "results" / "summary.json").read_text(encoding="utf-8"))


def text(name):
    return (ROOT / name).read_text(encoding="utf-8")


# Integrity

def test_official_files_names_sizes_hashes():
    assert sorted(p.name for p in D.RAW_DIR.iterdir()) == ["NEW.xlsx", "Spiral Stretch Data.sav"]
    sav, xlsx = D.RAW_DIR / "Spiral Stretch Data.sav", D.RAW_DIR / "NEW.xlsx"
    assert sav.stat().st_size == 4862 and xlsx.stat().st_size == 13848
    assert D.sha256sum(sav) == SPIRAL_SHA
    assert D.sha256sum(xlsx) == MAGNETO_SHA
    assert D.verify_raw() == {"Spiral Stretch Data.sav": SPIRAL_SHA, "NEW.xlsx": MAGNETO_SHA}


def test_verify_refuses_changed_file(tmp_path):
    bad = tmp_path / "raw"
    shutil.copytree(D.RAW_DIR, bad)
    with open(bad / "NEW.xlsx", "ab") as fh:
        fh.write(b"x")
    with pytest.raises(ValueError):
        D.verify_raw(bad)
    with pytest.raises(ValueError):
        D.load_raw("spiral", bad)


def test_hashes_recorded_in_provenance():
    p = text("PROVENANCE.md")
    assert SPIRAL_SHA in p and MAGNETO_SHA in p


def test_derived_csv_equal_official_files(frames):
    for k, name in D.DERIVED_NAMES.items():
        csv = pd.read_csv(D.DERIVED_DIR / name)
        raw = frames[k][0]
        assert list(csv.columns) == list(raw.columns)
        assert csv.shape == raw.shape
        np.testing.assert_allclose(csv.to_numpy(float), raw.to_numpy(float), rtol=0, atol=1e-9)


def test_dsverify_originals_untouched():
    base = Path("/workspace/dsverify")
    if not base.exists():
        pytest.skip("license check folder not on this machine")
    assert D.sha256sum(base / "dl_hnvhm376hg") == SPIRAL_SHA
    assert D.sha256sum(base / "dl_khdtg3rzmp") == MAGNETO_SHA
    assert (base / "meta_hnvhm376hg.txt").exists() and (base / "meta_khdtg3rzmp.txt").exists()


# Sample

def test_sample_sizes(frames):
    s, m = frames["spiral"][2], frames["magneto"][2]
    assert len(s) == 24 and s.group.value_counts().to_dict() == {1: 12, 2: 12}
    assert len(m) == 36 and m.group.value_counts().to_dict() == {1: 18, 2: 18}
    assert (s.age.min(), s.age.max()) == (30, 60)
    assert (m.age.min(), m.age.max()) == (32, 60)
    assert s.sex_code.value_counts().to_dict() == {2: 14, 1: 10}
    assert m.sex_code.value_counts().to_dict() == {1: 22, 2: 14}
    assert frames["spiral"][1]["value_labels"]["GENDER"] == {1.0: "MALE", 2.0: "FEMALE"}
    assert frames["spiral"][1]["value_labels"]["GROUP"] == {1.0: "EXPRIMENTAL", 2.0: "CONTROL"}


def test_no_minors(frames):
    for k in frames:
        assert frames[k][2].age.min() >= 18


def test_magneto_rom_set_has_adduction_spiral_does_not():
    assert "ADD" in D.outcome_keys("magneto") and "ADD" not in D.outcome_keys("spiral")
    assert len(D.outcome_keys("spiral")) == 7 and len(D.outcome_keys("magneto")) == 8


# No pooling

def test_analysis_refuses_mixed_trials(frames):
    mixed = pd.concat([frames["spiral"][2], frames["magneto"][2]], ignore_index=True)
    for fn in (A.baseline_table, A.within_group, A.contrasts, A.regularity, A.nprs_distribution):
        with pytest.raises(ValueError):
            fn(mixed)


def test_no_merge_or_concat_of_trial_rows_in_package():
    for p in (ROOT / "src" / "shoulder_capsulitis_lab").glob("*.py"):
        src = p.read_text(encoding="utf-8")
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and node.attr == "merge":
                pytest.fail(f"{p.name} uses .{node.attr}")
        assert "pd.concat" not in src or p.name == "analysis.py"


def test_outputs_have_no_pooled_rows(summary):
    assert summary["meta"]["pooled"] is False
    for t in (ROOT / "tables").glob("*.csv"):
        df = pd.read_csv(t)
        if "trial" in df.columns:
            assert set(df.trial.unique()) <= {"spiral", "magneto"}, t.name
            for c in ("n", "n1", "n2"):
                if c in df.columns:
                    assert df[c].max() <= 36, t.name
    side = pd.read_csv(ROOT / "tables" / "t11_side_by_side_no_pooling.csv")
    assert set(side.trial) == {"spiral", "magneto"}
    assert len(side) == 7 + 8
    assert set(summary["trials"]) == {"spiral", "magneto"}


def test_docs_never_describe_one_large_trial():
    for name in ["README.md", "RESULTS.md", "PORTFOLIO_BRIEF.md", "DISCUSSION.md"]:
        low = text(name).lower()
        assert "pooled" in low or "not pooled" in low or "never pooled" in low
        for bad in ["pooled estimate:", "combined effect:", "n=60", "n = 60", "60 participants", "60 people"]:
            assert bad not in low, (name, bad)
    assert "no results paper" in text("README.md").lower()


# Audit counts

def test_quality_flag_counts(audits):
    s, m = audits["spiral"]["facts"], audits["magneto"]["facts"]
    assert s["bmi_mismatch_gt_0_5"] == 13
    assert s["change_score_mismatches"] == 1
    cm = audits["spiral"]["change_mismatches"].iloc[0]
    assert cm.outcome == "FLEX" and cm.deposited_minus_recomputed == 5 and cm.group == 1
    assert (s["nprs_change_min"], s["nprs_change_max"]) == (3, 5)
    assert s["rows_improving_on_every_outcome"] == 24
    assert s["missing_values"] == 0 and s["outside_protocol_age"] == 0
    assert s["filter_artifact_matches_group1"] is True and s["diabetes_variable_present"] is False
    assert m["bmi_mismatch_gt_0_5"] == 3
    assert m["change_score_mismatches"] == 0
    assert m["outside_protocol_age"] == 19
    assert m["missing_values"] == 0
    assert m["repeated_spadi_pre_post_rows"] == 11 and m["repeated_spadi_pre_post_pairs"] == 4
    assert m["rows_improving_on_every_outcome"] == 36
    assert m["group_coding_documented"] is False


def test_flag_table_matches_audit():
    t = pd.read_csv(ROOT / "tables" / "t01_quality_flags.csv")
    get = lambda i: int(t.loc[t.flag_id == i, "count"].item())  # noqa: E731
    assert get("S2") == 13 and get("S3") == 1 and get("S4") == 24
    assert get("M2") == 3 and get("M3") == 19 and get("M6") == 0 and get("M7") == 11


# Numeric locks (from summary.json, regenerated by run_analysis.py)

def test_spiral_primary_numbers(summary):
    p = summary["trials"]["spiral"]["primary"]
    assert p["SPADI"]["diff"] == pytest.approx(11.2042, abs=1e-3)
    assert p["SPADI"]["diff_ci_low"] > 7 and p["SPADI"]["diff_ci_high"] < 15.5
    assert p["NPRS"]["diff"] == pytest.approx(1.4167, abs=1e-3)
    assert p["NPRS"]["diff_ci_low"] == pytest.approx(1.0, abs=0.1)
    assert p["FLEX"]["diff"] == pytest.approx(14.1667, abs=1e-3)
    for k, v in p.items():
        assert v["diff_ci_low"] > 0, k
        assert v["hedges_g"] > 1.1, k


def test_magneto_primary_numbers(summary):
    p = summary["trials"]["magneto"]["primary"]
    assert p["SPADI"]["diff"] == pytest.approx(1.7622, abs=1e-3)
    assert p["NPRS"]["diff"] == pytest.approx(-0.0556, abs=1e-3)
    assert p["FLEX"]["diff"] == pytest.approx(-1.0, abs=1e-3)
    for k, v in p.items():
        assert v["diff_ci_low"] < 0 < v["diff_ci_high"], k
    excl = [(name, k) for name, rows in summary["trials"]["magneto"]["sensitivity"].items()
            if not name.startswith("P:") for k, v in rows.items() if not v["diff_ci_low"] < 0 < v["diff_ci_high"]]
    assert excl == [("S3: repeated SPADI pairs, first occurrence only", "ADD")]
    v = summary["trials"]["magneto"]["sensitivity"][excl[0][0]]["ADD"]
    assert v["diff"] == pytest.approx(-2.1619, abs=1e-3) and v["diff_ci_high"] < 0


def test_point_estimates_recompute(frames):
    s = frames["spiral"][2]
    d = s.loc[s.group == 1, "imp_SPADI"].mean() - s.loc[s.group == 2, "imp_SPADI"].mean()
    assert d == pytest.approx(11.2042, abs=1e-3)
    m = frames["magneto"][2]
    d = m.loc[m.group == 1, "imp_NPRS"].mean() - m.loc[m.group == 2, "imp_NPRS"].mean()
    assert d == pytest.approx(-0.0556, abs=1e-3)


def test_spiral_sensitivities(summary):
    sens = summary["trials"]["spiral"]["sensitivity"]
    s1 = sens["S1: drop rows with BMI mismatch"]
    assert (s1["SPADI"]["n1"], s1["SPADI"]["n2"]) == (5, 6)
    assert s1["SPADI"]["diff_ci_low"] > 0 and s1["NPRS"]["diff_ci_low"] > 0
    s2 = sens["S2: deposited change scores (flexion error kept)"]
    assert s2["FLEX"]["diff"] == pytest.approx(14.5833, abs=1e-3)


def test_regularity_and_stress(summary):
    sp = summary["trials"]["spiral"]
    assert sp["post_values_fully_separated"]["FLEX"] and sp["post_values_fully_separated"]["ABD"]
    dist = sp["nprs_drop_distribution"]
    assert dist == {"1|4": 3, "1|5": 9, "2|3": 8, "2|4": 4}
    st = summary["stress_spiral"]
    assert st["NPRS|0"] == 1.0
    assert 0.3 < st["NPRS|1.5"] < 0.65
    assert st["NPRS|3"] < st["NPRS|1"]


def test_outputs_present(summary):
    assert len(list((ROOT / "tables").glob("*.csv"))) == 11
    pngs = sorted((ROOT / "figures").glob("*.png"))
    assert len(pngs) == 8
    for p in pngs:
        assert p.with_suffix(".webp").exists()


# License and wording

def test_attribution_and_cite_only():
    lic = text("DATA_LICENSE.md")
    for s in ["CC BY 4.0", "https://creativecommons.org/licenses/by/4.0/", "10.17632/hnvhm376hg.1",
              "10.17632/khdtg3rzmp.1", "Physiotherapy, Krishnagopal Mondal; Sharma, Sunita", "KUMAR, SAHIL; Pattnaik, Sandeep",
              "CC BY-NC-ND 4.0", "cited only", "not endorse", "Changes made", "10.7860/JCDR/2025/76129.20996",
              "10.7860/JCDR/2025/80478.21711"]:
        assert s in lic, s
    readme = text("README.md")
    assert "cited only" in readme and "have not endorsed" in readme
    assert "r93nz95zc7" not in readme


def test_ethics_statements():
    prov = text("PROVENANCE.md")
    assert "IEC-2994" in prov and "CTRI/2024/08/072699" in prov and "ClinicalTrials.gov" in prov
    assert "not verified" in prov
    assert "diabetes variable" in text("README.md")


def test_no_forbidden_dashes_names_or_emails():
    files = [ROOT / n for n in DOCS] + sorted((ROOT / "tables").glob("*.csv")) + [ROOT / "results" / "summary.json"]
    files += sorted((ROOT / "src").rglob("*.py")) + sorted((ROOT / "scripts").glob("*.py")) + sorted((ROOT / "tests").glob("*.py"))
    for p in files:
        t = p.read_text(encoding="utf-8")
        if p.name == "test_project.py":
            t = t.replace('"--"', "")
        for d in FORBIDDEN_DASHES:
            if p.suffix == ".py" and d == "--":
                # command line flags such as --download are allowed in code only
                continue
            assert d not in t, (p.name, repr(d))
        low = t.lower()
        for n in FORBIDDEN_NAMES:
            if p.name == "test_project.py":
                continue
            assert n not in low, (p.name, n)
        if p.name != "test_project.py":
            assert "@gmail" not in low and "e-mail:" not in low, p.name


def test_no_jcdr_text_copied():
    # Distinctive phrases from the protocols must not appear in our files.
    snippets = ["debilitating condition characterised by pain", "sequentially numbered opaque sealed envelopes",
                "high-quality evidence on the potential benefits"]
    for n in DOCS:
        low = text(n).lower()
        for s in snippets:
            assert s not in low, (n, s)


def test_only_expected_remote():
    if not (ROOT / ".git").exists():
        pytest.skip("no git repo")
    names = subprocess.run(["git", "-C", str(ROOT), "remote"], capture_output=True, text=True).stdout.split()
    assert set(names) <= {"origin"}
    for n in names:
        url = subprocess.run(["git", "-C", str(ROOT), "remote", "get-url", n], capture_output=True, text=True).stdout.strip()
        assert url.removesuffix(".git").endswith("github.com/victorgomezadapty/shoulder-capsulitis-lab"), url
