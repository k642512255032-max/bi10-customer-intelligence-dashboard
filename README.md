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

## Layout

A horizontal category bar across the top picks the family of figures; the left sidebar is
a slicer panel (segment, sub-segment, FHS tier, ES level, score ranges, priority, trigger,
product, province, stress/maturing/app flags). A KPI strip under the title reacts live to
the slicers, and each section is a two-column card grid.

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

## Data

The BI10 dataset is **generated, not real customer records**, so the full customer-level
sample is published here along with the aggregate tables.

| File | Size | What |
|---|---|---|
| `data/dashboard_sample.csv.gz` | 3.6 MB | 50,000 customer rows x 44 columns |
| `data/summary_metrics.json` | 93 KB | 136 metric keys, every population-level number |
| `data/*.csv` | ~20 KB | segment, sub-segment, matrix, opportunity, call-allocation, scorecard |

The sample is committed **gzipped**: the raw CSV is 42 MB, the gzip is 3.6 MB (8.5%), and
pandas reads `.csv.gz` natively with no code change. `config.sample_path()` prefers the
`.gz` and falls back to an uncompressed `dashboard_sample.csv` if you drop one in, so the
42 MB raw file stays git-ignored for local work.

Source pack: `RESULTS_PACK (3).zip`, 2026-10-18 09:18, produced by
`BI10_R02_FINAL_v5-4.ipynb`. Snapshot 4 Jun 2025, 1,000,528 customers,
**4 segments + 3 timing triggers**, 10 sub-segments.

## The one thing to know before changing the code

`dashboard_sample.csv` is **stratified**: exactly 5,000 rows per sub-segment (10 of them,
50,000 rows), whatever that sub-segment's real size. Raw shares from it are wrong -
unweighted it claims 11.7% of customers are in financial distress when the truth is 6.2%.

Every row carries a `W` weight (`real customers / 5,000`, ranging 4.76x to 41.8x) that
reweights the sample back to the population. Use `weighted_share()` and
`weighted_mean()` from `data_loader.py`; never `value_counts(normalize=True)`.
`tests/test_data_contract.py::test_unweighted_is_wrong` fails loudly if the weighting
is ever removed.

## Tests

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

19 data-contract tests covering the pack schema, the reweighting, the segment mapping,
and three honesty guards: the `Y_APPLY` selection artefact must stay inside an expander,
whole-base tables must never be filtered by segment, and the v5 `call_date_check` must
stay visible (it shows CALL timestamps do not line up with behaviour, so call-based
results are association, not prediction).
