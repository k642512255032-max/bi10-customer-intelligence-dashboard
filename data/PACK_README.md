# BI10 Round 02 – Customer Intelligence Engine (supporting files)

## Files
| File | Content |
|---|---|
| `BI10_R02_FINAL_v5.ipynb` | Full, reproducible analysis (data quality → cleaning → EDA → FHS → ES → segmentation & NBA → insights) |
| `outputs/customer_scores_nba.csv` | **Output dataset** – one row per customer (1,000,528 rows): FHS + tier + confidence + pillar scores + reason codes, ES + 5 dimensions + level, segment, Next Best Action (action, product, offer, channel, timing, priority) and a plain-English EXPLANATION |
| `outputs/fhs_scorecard.csv` | Full FHS scorecard: every factor, bin, observed bad rate and points (fully auditable) |
| `outputs/segment_profile.csv`, `opportunity_map.csv`, `call_allocation_by_segment.csv`, `matrix_fhs_es.csv` | Segment-level evidence tables |
| `outputs/figures/*.png` + `figure_index.csv` | All charts with captions and sources |
| `outputs/summary_metrics.json` | Every number quoted in the slides |

## Workflow
1. Data-quality audit (missing + hidden placeholders, time coverage, referential integrity, business-logic anomalies) → cleaning decisions D1–D10.
2. Cross-table harmonisation: product-family crosswalk, initiator taxonomy (PULL / WARM / PUSH), 247 call codes → 9 outcome classes.
3. Point-in-time feature engine (no look-ahead; label lags 120 / 365 days).
4. FHS = evidence-weighted scorecard (WoE + logistic weights), scale 60 = average applicant, +20 pts = half the odds of distress. Trained on loans applied 2023-03 → 2024-09, tested out-of-time.
5. ES = customer-initiated, time-decayed index (R/F/I/L/P weights chosen on a split-sample test, see `es_weights` in summary_metrics.json); call-based validation is read as association because call dates do not line up with customer events (D13).
6. FHS × ES → 4 segments (GROW · REACTIVATE · PROTECT · BUILD) + 3 timing triggers (live collections · just booked · loan maturing) → rule-based Next Best Action with risk guard-rails; 10 detailed sub-segments kept in SUB_SEGMENT.

## Reproduce
Put CALL.csv, CONTRACT.csv, CUSTOMER.csv, LEADS.csv, PAST_BEHAVIOR.csv in `MyDrive/BI10_DATA`, open the notebook in Google Colab, *Runtime → Run all* (~25–30 min, ~7 GB RAM). Snapshot: scored as of 4 Jun 2025 (data through 2025-06-04).
