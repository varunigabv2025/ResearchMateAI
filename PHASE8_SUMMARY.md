# Phase 8: Weighted RRF Experiment - Final Summary

**Date**: 2026-10-05  
**Status**: Complete - Ready for review (NOT committed)  
**Decision**: **Weighted RRF remains experimental - NOT adopted as production default**

---

## Implementation Complete ✅

### Modified Files (3)
1. **`backend/app/services/retrieval_service.py`** (+52 lines, -13 lines)
   - Added `DEFAULT_RRF_ALPHA = 1.0` and `DEFAULT_RRF_BETA = 1.0` constants
   - Modified `_reciprocal_rank_fusion()` to accept weighted parameters
   - Updated formula: `rrf_score = alpha/(rrf_k + rank_dense) + beta/(rrf_k + rank_lexical)`
   - Propagated weights through hybrid and reranked methods

2. **`backend/evaluation/run_evaluation.py`** (+34 lines, -9 lines)
   - Added `rrf_alpha` and `rrf_beta` to evaluator initialization
   - Added CLI arguments `--rrf-alpha` and `--rrf-beta`
   - Recorded weights in result output

3. **`backend/tests/test_hybrid_retrieval.py`** (+252 lines)
   - Added `TestWeightedRRF` class with 5 comprehensive tests
   - All 15 tests passing (10 existing + 5 new)

### Experiment Files (11)
- 3 Documentation reports (audit, implementation, verification)
- 3 Helper scripts (run experiments, summarize, verify)
- 4 Result JSON files (C0, W1, W2, W3)
- 1 Diagnostic script (from audit phase)

---

## Experimental Results

### Aggregate Metrics (10-question benchmark)

| Metric | C0 (α=1.0, β=1.0) | W1/W2/W3 (weighted) | Change |
|--------|-------------------|---------------------|--------|
| **Recall@10** | 0.722 | 0.778 | **+7.8%** |
| **Recall@3** | 0.315 | 0.519 | **+64.8%** |
| **Hit@5** | 0.556 | 0.667 | **+20.0%** |
| **MRR** | 0.534 | 0.523 | **-2.1%** |
| **Latency** | 279ms | ~270ms | Negligible |

**W1 (α=1.2, β=0.8), W2 (α=1.4, β=0.6), and W3 (α=1.6, β=0.4) produced IDENTICAL results.**

### Per-Question Results

| Question | C0 R@10 | Weighted R@10 | Impact |
|----------|---------|---------------|--------|
| q1 | 1.0 | 1.0 | ✅ Maintained |
| q2 | 1.0 | 1.0 (R@5: 1.0→0.667) | ⚠️ R@5 degraded |
| q3 | 0.5 | 0.0 | ❌ **Complete failure** |
| q4 | 0.0 | 1.0 | ✅ **Recovered** |
| q5 | 1.0 | 1.0 | ✅ Maintained |
| q6 | 1.0 (R@5: 0.0) | 1.0 (R@5: 1.0) | ✅ **Improved** |
| q7 | 0.0 | 0.0 | ❌ Failed |
| q8 | 1.0 (R@5: 0.0) | 1.0 (R@5: 0.5) | ✅ **Improved** |
| q9 | 1.0 | 1.0 | ✅ Maintained |
| q10 | N/A | N/A | N/A |

**Key Finding**: Weighted RRF partially improves retrieval coverage but does not establish an overall ranking improvement. Recall@10 increased from 72.2% to 77.8%, while MRR decreased from 0.534 to 0.523. q3 experienced a complete top-10 retrieval failure under weighted RRF. Therefore weighted RRF remains experimental and is not adopted as the production default.

---

## Why Not Production?

### Blocking Issues

1. **q3 complete retrieval failure**: q3 experienced a complete top-10 retrieval failure under weighted RRF, with Recall@10 decreasing from 0.5 to 0.0. Page 4, which was at rank 2 in C0, disappeared entirely from top-10 in weighted configs.

2. **MRR degradation**: -2.1% decrease indicates ranking inversions that may harm user experience despite improved recall.

3. **Trade-off, not improvement**: Improved coverage (Recall) at cost of ranking quality (MRR) and q3 failure.

4. **Benchmark too small**: 10 questions on 1 paper insufficient to validate general superiority.

### Hypothesis Evaluation

- **H1** (Weighted RRF improves dense-favored chunks): **PARTIALLY SUPPORTED** - works for q4/q6/q8, fails for q2/q3
- **H2** (Improves without degradation): **REJECTED** - material degradation observed (q3 failure, MRR decrease)
- **H3** (Useful config exists): **PARTIALLY SUPPORTED** - W1/W2/W3 equivalent; W1 most conservative

---

## Production Configuration (UNCHANGED)

```python
# Remains at equal weighting
DEFAULT_RRF_ALPHA = 1.0  # Dense weight
DEFAULT_RRF_BETA = 1.0   # Lexical weight
DEFAULT_DENSE_K = 20     # Dense candidate pool
DEFAULT_LEXICAL_K = 20   # Lexical candidate pool
DEFAULT_RRF_K = 60       # RRF constant
```

### Research Conclusion

**Weighted RRF partially supports the hypothesis that fusion weighting can improve relevant-chunk retrieval, but the observed MRR degradation and q3 regression prevent production adoption. The result requires validation on a larger multi-paper benchmark.**

---

## Weighted RRF Status: Experimental Feature

Available for research via CLI:
```bash
# Test weighted configurations
python evaluation/run_evaluation.py \
  --mode hybrid \
  --rrf-alpha 1.2 \
  --rrf-beta 0.8 \
  --skip-llm
```

---

## Next Steps (Phase 9 Candidates)

1. **Investigate q3 degradation** - Why did page 4 disappear?
2. **Expand benchmark** - 50-100 questions across 5-10 papers
3. **Adaptive weighting** - Per-query α/β based on characteristics
4. **Alternative fusion** - Score-based vs rank-based fusion

---

## Git Status

```
Branch: main
HEAD: 97f21d3
Status: NOT committed, NOT pushed

Modified files (3):
- backend/app/services/retrieval_service.py
- backend/evaluation/run_evaluation.py
- backend/tests/test_hybrid_retrieval.py

Untracked files (14):
- PHASE8_*.md (3 reports)
- backend/evaluation/*.py (3 scripts)
- backend/evaluation/results/phase8_*.json (5 results)
```

**Historical results unchanged. No secrets exposed. Dataset unchanged.**

---

## Tests Status

✅ **All 15 hybrid retrieval tests passing**
- 10 existing RRF tests (maintained)
- 5 new weighted RRF tests (added)

```
tests/test_hybrid_retrieval.py::TestReciprocalRankFusion - 10 passed
tests/test_hybrid_retrieval.py::TestWeightedRRF - 5 passed
```

---

## Ready for Review

Phase 8 implementation is complete with weighted RRF available as an experimental feature. Production defaults remain unchanged (α=1.0, β=1.0) due to q3 failure and MRR degradation.

**DO NOT COMMIT OR PUSH YET - awaiting final review**
