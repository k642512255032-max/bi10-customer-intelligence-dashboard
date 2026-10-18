"""Data-contract tests. These read the REAL pack on purpose: their job is to fail
loudly if the notebook is re-run and the export schema drifts."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from config import DATA_DIR, ES_LEVELS, FHS_TIERS, SEGMENTS, SUB_SEGMENTS  # noqa: E402
from data_loader import add_weights, split_table  # noqa: E402
from focus import SEGMENT_INDEXED, SEGMENT_SUBS, apply_focus  # noqa: E402
from formatting import auc_plain, pct, vnd  # noqa: E402
from strings import STRINGS  # noqa: E402

POP = 1_000_528


@pytest.fixture(scope="module")
def metrics():
    with open(DATA_DIR / "summary_metrics.json", encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="module")
def sub_profile():
    return pd.read_csv(DATA_DIR / "sub_segment_profile.csv", encoding="utf-8")


@pytest.fixture(scope="module")
def sample(sub_profile):
    path = DATA_DIR / "dashboard_sample.csv"
    if not path.exists():
        pytest.skip("customer-level sample not present (expected on a public deployment)")
    df = pd.read_csv(path, low_memory=False, encoding="utf-8")
    df["NBA_TRIGGER"] = df["NBA_TRIGGER"].fillna("None")
    df["PROVINCE"] = df["PROVINCE"].fillna("Unknown")
    return add_weights(df, sub_profile)


def _share(df, col):
    return df.groupby(col, observed=True)["W"].sum() / df["W"].sum()


# ---------------------------------------------------------------- schema
def test_sample_shape(sample):
    assert sample.shape[0] == 50_000          # 10 sub-segments x 5,000
    assert sample.shape[1] == 45              # 44 source columns + W


def test_stratification_holds(sample):
    counts = sample["SUB_SEGMENT"].value_counts()
    assert set(counts.index) == set(SUB_SEGMENTS)
    assert len(counts) == 10, "the v5 pack has 10 sub-segments"
    assert (counts == 5_000).all(), "the sample is stratified at 5,000 rows per sub-segment"


def test_matrix_total():
    m = pd.read_csv(DATA_DIR / "matrix_fhs_es.csv", encoding="utf-8").set_index("FHS_TIER")
    assert int(m.values.sum()) == POP
    assert set(m.index) == set(FHS_TIERS)
    assert set(m.columns) == set(ES_LEVELS)


def test_split_tables_parse(metrics):
    keys = [k for k, v in metrics.items()
            if isinstance(v, dict) and {"columns", "index", "data"} <= set(v)]
    assert len(keys) >= 20
    for k in keys:
        df = split_table(metrics, k)
        assert df.shape[0] > 0, k


# ---------------------------------------------------------------- G1: reweighting
def test_weights_sum_to_population(sample, metrics):
    assert abs(sample["W"].sum() - metrics["customers_total"]) < 1


def test_weighted_tier_matches_truth(sample, metrics):
    got = _share(sample, "FHS_TIER")
    truth = pd.Series(metrics["fhs_tier_mix"])
    assert (got - truth).abs().max() < 0.002


def test_weighted_level_matches_truth(sample, metrics):
    got = _share(sample, "ES_LEVEL")
    truth = pd.Series(metrics["es_level_mix"])
    assert (got - truth).abs().max() < 0.002


def test_unweighted_is_wrong(sample):
    """Guard: if someone removes the weighting this test is the alarm."""
    unweighted = sample["FHS_TIER"].value_counts(normalize=True)["Distressed"]
    assert unweighted > 0.10, "unweighted Distressed should be badly overstated (~11.7%)"
    weighted = _share(sample, "FHS_TIER")["Distressed"]
    assert weighted < 0.08, "weighted Distressed should be ~6.2%"


# ---------------------------------------------------------------- G: segment focus
def test_segment_mapping_complete(sub_profile):
    mapped = [s for subs in SEGMENT_SUBS.values() for s in subs]
    assert sorted(mapped) == sorted(SUB_SEGMENTS)
    assert set(SEGMENT_SUBS) == set(SEGMENTS)
    assert int(sub_profile["customers"].sum()) == POP


def test_focus_preserves_weights(sample):
    protect = apply_focus(sample, "PROTECT")
    got = _share(protect, "SUB_SEGMENT")
    expected = {"Silent Risk": 0.521, "Credit-Hungry Stressed": 0.205,
                "Credit-Hungry Newcomers": 0.155, "Stretched Seekers": 0.119}
    for k, v in expected.items():
        assert abs(got[k] - v) < 0.005, f"{k}: {got[k]:.3f} vs {v}"


def test_focus_unweighted_is_wrong(sample):
    protect = apply_focus(sample, "PROTECT")
    raw = protect["SUB_SEGMENT"].value_counts(normalize=True)["Stretched Seekers"]
    wtd = _share(protect, "SUB_SEGMENT")["Stretched Seekers"]
    assert raw > 0.20, "unweighted every sub-segment looks like 25% of PROTECT"
    assert wtd < 0.15, "truly Stretched Seekers is ~11.9% of PROTECT"


def test_segment_indexed_set(metrics):
    for key in SEGMENT_INDEXED:
        assert key in metrics, key
        idx = set(map(str, metrics[key]["index"]))
        assert idx & set(SEGMENTS), f"{key} is not actually segment-indexed"


def test_whole_base_tables_have_no_segment(metrics):
    """These must never be filtered by segment - they have no segment dimension."""
    for key in ["es_decile_outcomes", "es_monthly_forward", "fhs_validation",
                "es_walkforward", "I1_by_initiator", "I4_by_attempt"]:
        idx = set(map(str, metrics[key]["index"]))
        assert not (idx & set(SEGMENTS)), key


# ---------------------------------------------------------------- G2/G3: honesty guards
def test_dormant_rows_dropped(metrics):
    fwd = split_table(metrics, "es_forward_by_level").dropna(how="all")
    assert "Dormant" not in fwd.index


def test_yapply_is_quarantined():
    """Y_APPLY is a selection artefact; it may only appear inside an expander."""
    src = (ROOT / "sections" / "s3_es.py").read_text(encoding="utf-8")
    assert "es_backtest_by_level" in src
    before = src.split("es_backtest_by_level")[0]
    assert "st.expander" in before, "the artefact table must sit inside an expander"


# ---------------------------------------------------------------- misc
def test_strings_complete():
    bad = [k for k, v in STRINGS.items() if set(v) != {"vi", "en"} or not all(v.values())]
    assert not bad, bad


def test_vnd_formatting():
    assert vnd(0) == "-"
    assert vnd(float("nan")) == "-"
    assert vnd(8_800_000) == "8.8M VND"
    assert pct(0.3211) == "32.1%"
    assert "64" in auc_plain(0.6359, "en")


def test_call_date_check_present(metrics):
    """v5 added a sanity check showing CALL timestamps do not line up with behaviour.
    If it is ever reported as reliable, the forward evidence can be read as prediction;
    until then it is association only."""
    c = metrics["call_date_check"]
    assert "call_dates_reliable" in c
    assert c["share_with_application_within_14d_real"] > 0
    assert c["same_share_with_shuffled_call_dates"] > 0


def test_segment_counts_match_profile(sub_profile):
    from focus import SEGMENT_SUBS
    for seg, subs in SEGMENT_SUBS.items():
        a = sub_profile.loc[sub_profile.SUB_SEGMENT.isin(subs), "customers"].sum()
        b = sub_profile.loc[sub_profile.segment == seg, "customers"].sum()
        assert a == b, f"{seg}: mapping {a:,} vs pack {b:,}"
