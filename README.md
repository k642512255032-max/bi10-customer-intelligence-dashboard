# BI10 Customer Intelligence Dashboard

A bilingual (Vietnamese / English) Streamlit dashboard that explains the BI10 Round-02
customer-intelligence analysis to someone who has never seen the data.

Every number comes from the exported RESULTS_PACK of the BI10 Colab notebook.
Nothing is recomputed from raw data.

## What is in it

| Section | What it answers |
|---|---|
| 1. Start here | What is this data, and what did we build? |
| 2. Financial health (FHS) | Who repays safely, and how do we know? |
| 3. Engagement (ES) | Who is actually interested in us? |
| 4. FHS x ES | What happens when you cross the two scores? |
| 4b. Segment spotlight | Everything the pack knows about one segment |
| 5. What to do | The Next Best Action engine, plus a real-customer explorer |
| 6. Insights | Four findings nobody asked for |

Beginner-first conventions used on every page: a plain sentence before any chart, a
collapsed "how to read this" expander, and AUC always stated as "right about N times
out of 100" before the raw number.

## Segment focus

The sidebar can focus one segment (or one of the 8 sub-segments). Because the pack
ships population tables indexed by segment, focusing shows *real* numbers rather than
a reshaped sample. Each chart carries a badge saying which of three things it is doing:

- **filtered** - row-level sample, narrowed to the segment, with the whole base drawn behind as a ghost outline
- **highlighted** - population table, focused segment emphasised, the others dimmed for context
- **whole base** - the table has no segment dimension, so it is shown unchanged

## Running it

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app looks for data in `./data`, or in `$BI10_DATA_DIR` if that is set.

## Data, and what is deliberately not in this repo

Committed (no personal data, ~90 KB):
`summary_metrics.json`, `segment_profile.csv`, `sub_segment_profile.csv`,
`matrix_fhs_es.csv`, `opportunity_map.csv`, `call_allocation_by_segment.csv`,
`fhs_scorecard.csv`, `figure_index.csv`.

**Not committed:** `data/dashboard_sample.csv` - 40,000 real customer records with
income, province, debt ratio and credit ceiling. It is git-ignored on purpose. Without
it the app still runs; the distribution charts, the FHS x ES scatter and the customer
explorer show a notice instead. To get the full experience, extract
`dashboard_sample.csv` from your RESULTS_PACK into `data/`.

Source pack: `RESULTS_PACK_v3 (1).zip`, 2026-10-17 18:55, produced by
`BI10_R02_Notebook3_FINAL.ipynb`. Snapshot date 2025-06-05, 1,000,528 customers.

## The one thing to know before changing the code

`dashboard_sample.csv` is **stratified**: exactly 5,000 rows per sub-segment, whatever
that sub-segment's real size. Raw shares from it are wrong - unweighted it claims 14.2%
of customers are in financial distress when the truth is 6.2%.

Every row carries a `W` weight (`real customers / 5,000`, ranging 8.96x to 42.0x) that
reweights the sample back to the population. Use `weighted_share()` and
`weighted_mean()` from `data_loader.py`; never `value_counts(normalize=True)`.
`tests/test_data_contract.py::test_unweighted_is_wrong` fails loudly if the weighting
is ever removed.

## Tests

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

17 data-contract tests covering the pack schema, the reweighting, the segment mapping,
and two honesty guards (the `Y_APPLY` selection artefact must stay inside an expander;
whole-base tables must never be filtered by segment).
