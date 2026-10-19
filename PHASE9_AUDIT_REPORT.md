# Phase 9 Audit Report: Benchmark Expansion Strategy

**Date**: 2026-10-06  
**Phase**: 9 (Audit Only - No Implementation)  
**Branch**: main  
**HEAD**: e28d5bf (Phase 8 experiment artifacts)  
**Status**: AUDIT COMPLETE

---

## 1. Executive Summary

### Current State
ResearchMateAI has completed Phases 4-8, establishing:
- **Phase 4**: Dense retrieval baseline
- **Phase 5**: Hybrid (Dense + BM25 + RRF) with Recall@10 improving from ~46% to 72.2%
- **Phase 6**: Cross-encoder reranking (rejected due to MRR/Recall degradation and latency)
- **Phase 7**: Candidate pool expansion 20→50 (rejected - no quality improvement, +41.5% latency)
- **Phase 8**: Weighted RRF (experimental - improved Recall but degraded MRR, q3 failure)

### Critical Limitation
**All retrieval conclusions are based on a 10-question benchmark using a single 6-page paper.**

This limitation creates severe generalization risk:
- Small sample size (n=10)
- Single paper corpus
- Limited question-type diversity
- Potential overfitting to specific retrieval characteristics
- No evidence that findings generalize to different papers or question types

### Phase 9 Objective
**Design a scientifically defensible benchmark expansion strategy to test whether Phase 4-8 conclusions generalize across multiple papers and diverse question types.**

### Key Finding: INSUFFICIENT CORPUS
**The database contains only 1 unique paper (PA-EIS IEEE, 6 pages, 54 chunks), uploaded twice as duplicates.**

**This severely limits benchmark expansion options.**

---

## 2. Current Benchmark Structure

### Dataset File
- **Location**: `backend/evaluation/dataset.json`
- **Name**: "PA-EIS Evaluation Dataset"
- **Paper**: PA-EIS (Priority-Aware Edge Inference Scheduling) IEEE paper
- **Questions**: 10
- **Created**: 2026-10-04

### Schema
```json
{
  "dataset_name": string,
  "paper_id": string,
  "description": string,
  "created": string,
  "questions": [
    {
      "id": string,
      "question": string,
      "category": string,
      "expected_answer_contains": string[],
      "relevant_pages": int[],
      "answerable": boolean,
      "notes": string
    }
  ]
}
```

### Ground Truth Methodology
Current approach:
- **Relevant pages** specified explicitly (human-labeled)
- **Expected keywords** for answer validation
- **Answerability flag** (q10 explicitly unanswerable)
- **Category labels** for question classification

### Evaluation Metrics (Current)
- **Hit Rate @1/3/5/10**: Whether any relevant page retrieved
- **Recall @1/3/5/10**: Proportion of relevant pages retrieved
- **Precision @1/3/5/10**: Proportion of retrieved pages that are relevant
- **MRR**: Mean Reciprocal Rank of first relevant result
- **Latency**: Retrieval time (mean, median, std dev)

---

## 3. Current Corpus Inventory

### Database Status
```
Total papers: 2
  Paper 1: 075cdd7f-bff1-43fd-a52c-bba13a64acda
    Original filename: PA-EIS_IEEE_first5pages.pdf
    Pages: 6
    Chunks: 54
    Processed: True
  
  Paper 2: bd38227a-c1c7-4308-aa62-125a1bbd700f
    Original filename: PA-EIS_IEEE_first5pages.pdf
    Pages: 6
    Chunks: 54
    Processed: True

CRITICAL: Both papers are DUPLICATES of the same file.
```

### Available Unique Papers
**Only 1 unique paper:**
- **PA-EIS IEEE paper** (Priority-Aware Edge Inference Scheduling)
- **Pages**: 6 (first 5 pages + 1 additional)
- **Chunks**: 54
- **Content**: Containerized Linux edge nodes, CFS scheduling, inference workloads
- **Domain**: Computer Science / Systems / Edge Computing

### Sample Chunk Content Quality
```
Page 1, Chunk 0: "Priority-Aware Operating System Scheduling for 
Concurrent Edge AI Inference Workloads: An Empirical 
Study on Container..."

Page 1, Chunk 1: "scheduler rather than by the model itself. Linux allocates CPU time 
through the Completely Fair Scheduler (CFS), which ..."

Page 1, Chunk 2: "round containers, and in which the scheduling weight 
and nice value assigned to inference are swept over a defined grid..."
```

**Quality Assessment**: Chunks contain coherent technical content suitable for factual and methodological questions.

---

## 4. Existing 10-Question Analysis

### Question Distribution by Category

| Category | Count | Questions |
|----------|-------|-----------|
| motivation | 1 | q1 |
| methodology | 1 | q2 |
| dataset | 1 | q3 |
| results | 1 | q4 |
| limitations | 1 | q5 |
| technical_detail | 1 | q6 |
| conceptual | 1 | q7 |
| multi_part | 1 | q8 |
| comparison_inference | 1 | q9 |
| out_of_scope | 1 | q10 |

**Observation**: Perfect balance across 10 categories. Each question tests a different aspect.

### Detailed Question Analysis

| ID | Question | Type | Pages | R@5 | R@10 | MRR | Known Issues |
|----|----------|------|-------|-----|------|-----|--------------|
| q1 | Main motivation for containerised Linux edge nodes? | factual/motivation | 1, 2 | 1.0 | 1.0 | 1.0 | ✅ None |
| q2 | What methodology does PA-EIS use? | methodological | 1, 2, 3 | 1.0 | 1.0 | 0.33 | ⚠️ Multi-page, rank variation |
| q3 | What workloads used for evaluation? | factual/dataset | 3, 4 | 0.0 | 0.5 | 0.5 | ❌ **q3 failure in weighted RRF** |
| q4 | Reported evaluation results/metrics? | results/negative | 4 | 0.0 | 0.0 | 0.0 | ❌ **Dense+Hybrid failure** (recovered in W1) |
| q5 | What limitations explicitly mentioned? | limitations | 4, 5 | 1.0 | 1.0 | 1.0 | ✅ None |
| q6 | Linux kernel features PA-EIS relies on? | technical_detail | 3 | 1.0 | 1.0 | 0.5 | ⚠️ Rank variation (improved in W1) |
| q7 | Why restrict CPU cores intentionally? | conceptual/rationale | 3 | 0.0 | 0.0 | 0.0 | ❌ **All configs fail** |
| q8 | Container technology and what it enables? | multi-part/connection | 3, 4 | 0.0 | 1.0 | 0.2 | ⚠️ Multi-part (improved in W1) |
| q9 | How PA-EIS differs from traditional OS? | synthesis/comparison | 1, 2, 3 | 1.0 | 1.0 | 1.0 | ✅ None |
| q10 | Paper's stance on neural architecture search? | out_of_scope | none | N/A | N/A | N/A | ✅ Correctly unanswerable |

### Difficulty Classification

**Easy (5)**: q1, q5, q9, q10
- Single-concept factual questions
- Broad section coverage
- Multiple relevant chunks
- High Recall@5/10

**Medium (2)**: q2, q6
- Multi-page questions
- Specific technical details
- Moderate ranking variation

**Hard (3)**: q3, q4, q7, q8
- Single-page or narrow scope
- Specific terminology or metrics
- Dense/Hybrid baseline failures
- Require precise chunk matching

### Retrieval Characteristics

**Multi-page questions**: q1, q2, q8, q9 (4/10 = 40%)
**Single-page questions**: q3, q4, q6, q7 (4/10 = 40%)
**Out-of-scope**: q10 (1/10 = 10%)

**Ground truth span**:
- 2 pages: q1, q3, q8
- 3 pages: q2, q9
- 1 page: q4, q6, q7
- 2 pages: q5
- 0 pages: q10

---

## 5. Benchmark Diversity Analysis

### What the Current Benchmark Covers

✅ **Question type diversity**: 10 distinct categories  
✅ **Difficulty range**: Easy, medium, hard questions  
✅ **Multi-page questions**: 40% require information across pages  
✅ **Negative cases**: q10 tests out-of-scope handling  
✅ **Factual + conceptual + methodological coverage**

### Critical Gaps

❌ **Single paper only**: No cross-paper comparison possible  
❌ **Small sample size**: 10 questions insufficient for statistical confidence  
❌ **Domain-specific**: Only systems/edge computing domain  
❌ **Short paper**: 6 pages limits question complexity  
❌ **No multi-document questions**: Cannot test cross-paper retrieval  
❌ **Limited numerical questions**: q4 is the only metrics-focused question  
❌ **No table/figure questions**: Visual content not tested  
❌ **Potential overfitting**: Retrieval optimized for this specific paper's structure

---

## 6. Available-Paper Suitability Assessment

### Paper 1: PA-EIS IEEE (Priority-Aware Edge Inference Scheduling)

**Status**: SUITABLE (currently used)

**Strengths**:
- ✅ 54 chunks provide good retrieval diversity
- ✅ Technical content enables factual/methodological questions
- ✅ 6 pages span multiple sections
- ✅ Clear structure (motivation, methodology, evaluation)
- ✅ Specific terminology enables precise ground truth
- ✅ Already has 10 validated questions with ground truth

**Limitations**:
- ⚠️ Only 6 pages (relatively short)
- ⚠️ Evaluation section incomplete (results "not reported")
- ⚠️ Systems/edge computing domain (narrow)

**Expansion Potential**:
Can support 10-15 additional questions covering:
- More technical details (cgroups, scheduling parameters)
- Experimental design questions
- Background/related work questions
- Limitation/future work questions

**Estimated Additional Questions**: 10-15 (total 20-25 for this paper)

### Additional Papers Needed

**None currently available in database.**

To achieve a robust multi-paper benchmark, need:
- **Minimum**: 4 more papers (5 total)
- **Ideal**: 9 more papers (10 total)

**Required paper characteristics**:
- Similar length (5-15 pages)
- Computer science / AI / ML domains
- Clear technical content
- Processable PDF format
- Ability to establish reliable ground truth

**Domains to target for diversity**:
- Machine learning (model training, architectures)
- Natural language processing
- Computer vision
- Distributed systems
- Databases
- Security

---

## 7. Proposed Expanded Benchmark

### Constraint-Based Target

**Current limitation**: Only 1 unique paper available

**Option A: Single-Paper Expansion (Immediate)**
- Expand PA-EIS paper from 10 → 25 questions
- Target: **25 questions, 1 paper**
- Timeline: Can execute immediately
- Risk: Does NOT address cross-paper generalization

**Option B: Multi-Paper Expansion (Requires New Data)**
- Acquire 4-9 additional papers
- Target: **50-60 questions across 5-10 papers**
- Timeline: Requires paper acquisition and processing
- Benefit: Tests cross-paper generalization

**Option C: Hybrid Approach (Recommended)**
- Phase 9a: Expand PA-EIS to 25 questions (Benchmark A expansion)
- Phase 9b: Acquire papers and create 50-question multi-paper benchmark (Benchmark B)
- Timeline: 9a immediate, 9b deferred pending data acquisition

### Recommended Target (Option C)

**Phase 9a: Benchmark A Expansion**
- Questions: 10 → 25 (+15 new questions)
- Papers: 1 (PA-EIS only)
- Purpose: Test whether Phase 8 conclusions are robust within the same paper
- Can validate: Question-type effects, difficulty effects
- Cannot validate: Cross-paper generalization

**Phase 9b: Benchmark B Creation** (future)
- Questions: 50-60
- Papers: 5-10
- Purpose: Full cross-paper generalization test
- Can validate: All Phase 4-8 conclusions across diverse corpus

---

## 8. Question-Type Distribution (Proposed for Benchmark A Expansion)

### Proposed 25-Question Distribution (PA-EIS Paper)

| Category | Current | Proposed | New Questions |
|----------|---------|----------|---------------|
| Factual (motivation, background) | 1 | 3 | +2 |
| Methodology | 1 | 3 | +2 |
| Technical details | 1 | 4 | +3 |
| Evaluation/dataset | 1 | 3 | +2 |
| Results/metrics | 1 | 2 | +1 |
| Limitations/future work | 1 | 2 | +1 |
| Conceptual/rationale | 1 | 3 | +2 |
| Multi-part/synthesis | 1 | 3 | +2 |
| Out-of-scope | 1 | 2 | +1 |
| **Total** | **10** | **25** | **+15** |

### Rationale
- Maintains category balance
- Increases sample size per category
- Enables within-category performance analysis
- Tests retrieval robustness to question phrasing variations

---

## 9. Difficulty Distribution (Proposed)

### Target Distribution for 25 Questions

- **Easy** (5 current → 8 proposed): +3
  - Broad questions, multi-chunk answers
  - Clear ground truth across multiple pages
  
- **Medium** (2 current → 10 proposed): +8
  - Specific technical details
  - Single-section focus
  - Moderate ranking sensitivity

- **Hard** (3 current → 7 proposed): +4
  - Narrow scope, precise terminology
  - Single-chunk answers
  - Known retrieval challenges

**Target Distribution**: 32% easy, 40% medium, 28% hard

### Rationale
- Shifts toward medium difficulty (most realistic)
- Maintains hard questions to test system limits
- Provides sufficient easy questions for baseline validation

---

## 10. Ground-Truth Methodology

### Proposed Rigorous Approach

**Step 1: Question Creation**
- Author creates candidate question
- Manually identifies relevant pages
- Manually identifies relevant chunks (by reading)
- Documents expected answer elements

**Step 2: Ground-Truth Validation**
- For each question, retrieve top-20 chunks using current system
- Manually review ALL top-20 chunks
- Mark each chunk as RELEVANT / PARTIALLY RELEVANT / NOT RELEVANT
- Document reasoning for borderline cases

**Step 3: Relevance Criteria**
A chunk is RELEVANT if it:
- Directly answers the question, OR
- Provides essential context for the answer, OR
- Contains key terminology/concepts mentioned in the question

A chunk is PARTIALLY RELEVANT if it:
- Mentions related concepts but doesn't directly answer
- Provides background but not core answer

A chunk is NOT RELEVANT if it:
- Does not relate to the question topic

**Step 4: Exclusion Criteria**
Exclude questions where:
- Ground truth cannot be confidently established
- Question is ambiguous
- Answer requires external knowledge
- Multiple valid interpretations exist

**Step 5: Documentation**
For each question, record:
```json
{
  "question_id": "q11",
  "question": "...",
  "category": "...",
  "difficulty": "easy|medium|hard",
  "relevant_pages": [1, 2],
  "relevant_chunks": ["chunk_id_1", "chunk_id_2"],
  "partially_relevant_chunks": ["chunk_id_3"],
  "expected_answer_keywords": ["keyword1", "keyword2"],
  "answerable": true,
  "ground_truth_confidence": "high|medium|low",
  "notes": "..."
}
```

### No LLM-Generated Ground Truth
**All ground truth must be human-verified by reading the source chunks.**

---

## 11. Contamination Risks

### Identified Risks

1. **Filename Leakage**
   - Current paper filename: "PA-EIS_IEEE_first5pages.pdf"
   - Leaks: "PA-EIS" (paper acronym), "IEEE", "first5pages"
   - Risk: Medium
   - Mitigation: Anonymize filenames during evaluation

2. **Page Number Leakage**
   - Ground truth specifies explicit page numbers
   - Risk: Low (page numbers needed for evaluation)
   - Mitigation: None needed

3. **Question Wording Overlap**
   - Questions may contain exact phrases from paper
   - Risk: Medium
   - Example: "What workloads are used for evaluation?" may overlap with "Evaluation" section heading
   - Mitigation: Test with BM25 lexical search to detect high-overlap questions

4. **Duplicate Papers**
   - Current database has duplicate PA-EIS papers
   - Risk: High (could artificially inflate retrieval metrics)
   - Mitigation: **Remove duplicate paper before Phase 9 evaluation**

5. **Chunk Deduplication**
   - Same text may appear in multiple chunks (overlap)
   - Risk: Low (overlap is intentional for context)
   - Mitigation: Verify overlap doesn't create artificial relevance

6. **Section Name Leakage**
   - Chunks include section names
   - Risk: Low (sections provide valid context)
   - Mitigation: None needed

### Safeguards

✅ **Remove duplicate paper 2 before evaluation**  
✅ **Manual ground-truth validation (no LLM generation)**  
✅ **Test lexical overlap between questions and chunks**  
✅ **Document high-overlap cases**  
✅ **Report per-question contamination risk**

---

## 12. Evaluation Matrix (Phase 9a)

### Configurations to Compare

Using expanded 25-question benchmark on PA-EIS paper:

| Config ID | Name | Description | Parameters |
|-----------|------|-------------|------------|
| **A** | Dense Baseline | Dense-only retrieval | top_k=5 |
| **B** | Hybrid 20+20 | Dense + BM25 + RRF | dense_k=20, lexical_k=20, α=1.0, β=1.0 |
| **C** | Weighted W1 | Weighted RRF (conservative) | dense_k=20, lexical_k=20, α=1.2, β=0.8 |
| **D** | Weighted W2 | Weighted RRF (moderate) | dense_k=20, lexical_k=20, α=1.4, β=0.6 |
| **E** | Weighted W3 | Weighted RRF (aggressive) | dense_k=20, lexical_k=20, α=1.6, β=0.4 |
| **F** | Reranked | Hybrid + Cross-encoder | hybrid + rerank (optional) |

### Metrics to Report

**Per-Configuration Metrics**:
- Hit Rate @1, @3, @5, @10
- Recall @1, @3, @5, @10
- Precision @1, @3, @5, @10
- MRR
- Latency (mean, median, std dev, min, max)

**Per-Question Metrics**:
- Recall @5, @10
- MRR
- Retrieved pages
- Change vs baseline (A)

**Per-Category Metrics**:
- Average Recall @10 per question category
- Identifies which question types benefit from each configuration

**Per-Difficulty Metrics**:
- Average Recall @10 for easy/medium/hard
- Tests whether weighted RRF helps harder questions

---

## 13. Metrics and Reporting Methodology

### Statistical Considerations

**Sample Size**: 25 questions (still relatively small)

**Reporting Requirements**:
1. **Absolute metric values** (e.g., Recall@10 = 0.76)
2. **Percentage-point changes** (e.g., +4.0 pp, not "+5.5%")
3. **Per-question win/loss counts** (e.g., "improved 15/25, degraded 3/25, unchanged 7/25")
4. **Per-category breakdowns**
5. **Confidence qualifiers**: "on this 25-question benchmark" (avoid overgeneralization)

### No Statistical Significance Claims

**With n=25, do NOT claim**:
- "Statistically significant improvement"
- "Confidence interval: ..."
- "p-value < 0.05"

**Instead, report**:
- "Improved on 18/25 questions"
- "Average Recall@10 increased 5.2 percentage points"
- "Consistent improvement across 8/9 question categories"

### Uncertainty Acknowledgment

All conclusions must be qualified:
- "On this single-paper, 25-question benchmark..."
- "Within the PA-EIS paper domain..."
- "Generalization to other papers remains untested..."

---

## 14. Success Criteria

### Phase 9a Goals (25-Question Benchmark)

**Primary Research Question**:
"Do the Phase 8 findings (weighted RRF trade-offs) replicate with a larger question set on the same paper?"

**Success Criteria**:

1. **Hybrid vs Dense** (validate Phase 5 finding)
   - Recall@10 improvement ≥5 percentage points
   - Consistent across ≥80% of questions
   - Consistent across all question categories

2. **Weighted RRF vs Standard RRF** (validate Phase 8 finding)
   - Recall@10 improvement confirmed
   - MRR degradation confirmed or refuted
   - Failure pattern (q3-like) occurs in <10% of questions

3. **W1/W2/W3 Equivalence** (test Phase 8 observation)
   - Check whether W1/W2/W3 remain identical
   - If different, identify which questions differentiate them

4. **Question-Type Effects**
   - Identify which categories benefit most from weighted RRF
   - Identify which categories suffer from weighted RRF

5. **Difficulty Effects**
   - Check whether weighted RRF improves hard questions
   - Check whether weighted RRF degrades easy questions

### What Success Does NOT Mean

❌ "Weighted RRF is production-ready"  
❌ "Findings generalize to all papers"  
❌ "System is optimal"

✅ "Weighted RRF trade-offs replicate within PA-EIS paper"  
✅ "Hybrid consistently outperforms Dense on this paper"  
✅ "Identified question types that benefit/suffer from weighting"

---

## 15. Recommended Benchmark Structure

### Proposal: Two-Tier Benchmark System

**Benchmark A: Original + Expanded (PA-EIS Paper)**
- **Questions**: 25 (10 original + 15 new)
- **Papers**: 1 (PA-EIS)
- **Purpose**: Question-type and difficulty analysis within single paper
- **Status**: Can be created immediately

**Benchmark B: Multi-Paper Generalization (Future)**
- **Questions**: 50-60
- **Papers**: 5-10 (requires acquisition)
- **Purpose**: Cross-paper and cross-domain generalization
- **Status**: Deferred pending paper acquisition

### Preserve Historical Benchmark A (10 Questions)

**Keep original 10 questions unchanged as "Benchmark A-Original"**

Reasons:
- Preserves historical Phase 4-8 comparisons
- Enables longitudinal tracking
- Provides stable reference point
- Allows before/after analysis of benchmark expansion effects

**New 15 questions become "Benchmark A-Extended"**

**Combined 25 questions = "Benchmark A-Full"**

### File Structure

```
backend/evaluation/
├── dataset_original.json          # Original 10 questions (frozen)
├── dataset_expanded.json          # Full 25 questions
├── results/
│   ├── phase4_dense_10q.json     # Historical (preserved)
│   ├── phase5_hybrid_10q.json    # Historical (preserved)
│   ├── phase8_rrf_control_10q.json    # Historical (preserved)
│   ├── phase9a_dense_25q.json         # New
│   ├── phase9a_hybrid_25q.json        # New
│   ├── phase9a_weighted_w1_25q.json   # New
│   └── ...
```

---

## 16. Phase 9 Experimental Plan

### Phase 9a: Single-Paper Expansion (Immediate)

**Step 1: Create 15 New Questions**
- Target PA-EIS paper
- Follow ground-truth methodology (Section 10)
- Maintain category/difficulty distribution (Sections 8, 9)
- Validate against contamination risks (Section 11)
- Timeline: 2-4 hours of manual work

**Step 2: Remove Duplicate Paper**
- Delete paper ID `bd38227a-c1c7-4308-aa62-125a1bbd700f`
- Verify only one PA-EIS paper remains
- Prevents contamination risk

**Step 3: Run Evaluation Matrix**
- Execute configs A, B, C, D, E on 25-question benchmark
- Skip config F (reranking) unless explicitly requested
- Estimated time: 5 runs × 25 questions × ~0.3s = ~40 seconds per run

**Step 4: Analysis**
- Compare 10-question vs 25-question results
- Per-question analysis (25 questions)
- Per-category analysis
- Per-difficulty analysis
- Validate/refute Phase 8 findings

**Step 5: Documentation**
- Create `PHASE9A_IMPLEMENTATION_REPORT.md`
- Document findings
- Identify limitations
- Recommend Phase 9b scope

### Phase 9b: Multi-Paper Expansion (Future)

**Prerequisites**:
- Acquire 4-9 additional research papers
- Process papers (PDF → chunks → embeddings)
- Create 40-50 new questions across papers

**Timeline**: Deferred pending paper acquisition

---

## 17. Expected Research Contribution

### Phase 9a Contributions

1. **Validation of Phase 8 Findings**
   - Tests whether weighted RRF trade-offs (Recall ↑, MRR ↓) replicate
   - Tests whether q3-like failures are systematic or isolated
   - Tests whether W1/W2/W3 equivalence persists

2. **Question-Type Analysis**
   - Identifies which categories benefit from weighted RRF
   - Identifies which categories suffer from weighted RRF
   - Enables targeted retrieval strategy selection

3. **Difficulty Analysis**
   - Tests whether weighted RRF improves hard questions
   - Tests whether hybrid consistently helps easy questions

4. **Robustness Testing**
   - 2.5× larger sample (10 → 25 questions)
   - More stable metric estimates
   - Reduced sampling noise

5. **Benchmark Quality Improvement**
   - Validates evaluation methodology
   - Identifies edge cases
   - Improves ground-truth process

### Phase 9a Limitations

- ❌ Does NOT test cross-paper generalization
- ❌ Does NOT test cross-domain generalization
- ❌ Still single-paper corpus
- ❌ Small sample (n=25) limits statistical confidence
- ❌ Overfitting risk remains

### Phase 9b Contributions (Future)

- ✅ Cross-paper generalization
- ✅ Cross-domain generalization
- ✅ Larger sample (n=50-60)
- ✅ Tests paper-length effects
- ✅ Tests domain-specific retrieval challenges
- ✅ Enables multi-document retrieval testing

---

## 18. Files That Would Need Modification

### Phase 9a Implementation (No Changes Yet)

**New Files to Create**:
1. `backend/evaluation/dataset_expanded.json` (25 questions)
2. `backend/evaluation/results/phase9a_dense_25q.json`
3. `backend/evaluation/results/phase9a_hybrid_25q.json`
4. `backend/evaluation/results/phase9a_weighted_w1_25q.json`
5. `backend/evaluation/results/phase9a_weighted_w2_25q.json`
6. `backend/evaluation/results/phase9a_weighted_w3_25q.json`
7. `PHASE9A_IMPLEMENTATION_REPORT.md`

**Files to Preserve (No Modification)**:
- `backend/evaluation/dataset.json` (original 10 questions) → rename to `dataset_original.json`
- All Phase 4-8 result files (preserved as historical)
- `backend/app/services/retrieval_service.py` (no code changes)
- `backend/evaluation/run_evaluation.py` (no code changes)

**Database Changes**:
- Delete duplicate paper 2 (`bd38227a-c1c7-4308-aa62-125a1bbd700f`)
- No schema changes
- No embedding regeneration needed

**Production Configuration**:
- NO CHANGES (remains α=1.0, β=1.0, hybrid default)

---

## 19. Risks and Limitations

### Phase 9a Risks

1. **Insufficient Generalization**
   - Risk: HIGH
   - Single paper limits external validity
   - Findings may not transfer to other papers
   - Mitigation: Explicitly state limitation in all reporting

2. **Overfitting to PA-EIS Paper**
   - Risk: MEDIUM
   - Retrieval system may have implicitly optimized for this paper during Phases 4-8
   - New questions on same paper don't eliminate this
   - Mitigation: Phase 9b multi-paper benchmark needed

3. **Small Sample Size**
   - Risk: MEDIUM
   - n=25 still relatively small
   - Metric noise remains
   - Outlier questions have disproportionate impact
   - Mitigation: Report per-question details, avoid overgeneralization

4. **Ground-Truth Subjectivity**
   - Risk: MEDIUM
   - Human labeling introduces bias
   - Borderline relevance cases are subjective
   - Mitigation: Document reasoning, mark low-confidence cases

5. **Question Creation Bias**
   - Risk: LOW-MEDIUM
   - New questions may unconsciously favor certain retrieval strategies
   - Mitigation: Create questions before running evaluation

6. **Contamination**
   - Risk: MEDIUM
   - Duplicate paper currently in database
   - Filename leakage
   - Mitigation: Remove duplicate, anonymize filenames

### Mitigation Strategy

✅ **Acknowledge limitations explicitly in all reporting**  
✅ **Treat Phase 9a as validation, not proof of generalization**  
✅ **Use Phase 9a to refine ground-truth methodology for Phase 9b**  
✅ **Plan Phase 9b multi-paper benchmark**

---

## 20. Git Status

### Current State
```
Branch: main
HEAD: e28d5bf (chore(phase8): preserve weighted RRF experiment artifacts)
Working tree: clean
```

### Phase 9 Audit Status
- ✅ No code modified
- ✅ No datasets modified
- ✅ No results modified
- ✅ No commits made
- ✅ Only audit report created: `PHASE9_AUDIT_REPORT.md`

### Files Created (Audit Only)
- `PHASE9_AUDIT_REPORT.md` (this file)

### Production Configuration (Unchanged)
```python
DEFAULT_RRF_ALPHA = 1.0
DEFAULT_RRF_BETA = 1.0
DEFAULT_DENSE_K = 20
DEFAULT_LEXICAL_K = 20
DEFAULT_RRF_K = 60
```

---

## PHASE 9 RECOMMENDATION

### Recommended Strategy

**TWO-PHASE APPROACH:**

**Phase 9a (Immediate): Single-Paper Expansion**
- Expand PA-EIS benchmark from 10 → 25 questions
- Run evaluation matrix (Dense, Hybrid, W1, W2, W3)
- Validate Phase 8 findings within-paper
- Analyze question-type and difficulty effects
- Timeline: Can execute immediately

**Phase 9b (Future): Multi-Paper Generalization**
- Acquire 4-9 additional research papers
- Create 50-60 question benchmark across 5-10 papers
- Test cross-paper and cross-domain generalization
- Timeline: Deferred pending paper acquisition

### Target

**Phase 9a:**
- **Questions**: 25 (10 existing + 15 new)
- **Papers**: 1 (PA-EIS only)
- **Configurations**: 5 (Dense, Hybrid, W1, W2, W3)

**Phase 9b (Future):**
- **Questions**: 50-60
- **Papers**: 5-10 (requires acquisition)
- **Configurations**: Same as 9a

### Why This Approach

**Evidence-Based Reasoning:**
1. **Only 1 unique paper available** (database contains duplicates)
2. **Cannot test cross-paper generalization without additional papers**
3. **Phase 9a provides immediate value**: validates Phase 8 within-paper, tests question-type effects
4. **Phase 9a informs Phase 9b**: refines ground-truth methodology, identifies challenging question types
5. **Two-phase approach is pragmatic**: makes progress now, defers multi-paper work until corpus is ready

**Phase 9a Alone is NOT Sufficient**:
- Does not prove generalization
- Does not eliminate overfitting risk
- Does not test cross-paper retrieval
- But provides valuable within-paper analysis

**Phase 9b is Essential for Generalization Claims**:
- Tests whether hybrid consistently beats dense across papers
- Tests whether weighted RRF trade-offs are universal
- Tests domain-specific retrieval challenges
- Enables production-readiness decision

### Benchmark A (Original 10 Questions)

**PRESERVE AS HISTORICAL REFERENCE**
- Rename to `dataset_original.json`
- Never modify
- Enables Phase 4-8 historical comparison
- Provides longitudinal tracking

### Benchmark B (Expanded 25 Questions)

**CREATE AS "BENCHMARK A-FULL"**
- Contains original 10 + 15 new questions
- Enables Phase 9a within-paper analysis
- Tests question-type and difficulty effects
- File: `dataset_expanded.json`

### Benchmark C (Future 50-60 Questions, Multi-Paper)

**CREATE AS "BENCHMARK B" (Phase 9b)**
- 50-60 questions across 5-10 papers
- Tests cross-paper generalization
- Requires paper acquisition first
- Timeline: TBD

### Confidence

**MEDIUM**

**Rationale**:
- ✅ Phase 9a scope is well-defined and executable
- ✅ Ground-truth methodology is rigorous
- ✅ Evaluation matrix is comprehensive
- ⚠️ Phase 9a alone provides limited generalization evidence
- ⚠️ Phase 9b timeline uncertain (depends on paper acquisition)
- ❌ Database limitation (1 paper) is severe

**Recommendation Strength**: Phase 9a should proceed immediately. Phase 9b planning should begin in parallel (paper acquisition).

---

## Appendix: Next Steps (If Approved)

### Immediate Actions (Phase 9a)

1. **Remove duplicate paper** from database
   ```sql
   DELETE FROM papers WHERE id = 'bd38227a-c1c7-4308-aa62-125a1bbd700f';
   ```

2. **Rename original dataset**
   ```bash
   mv dataset.json dataset_original.json
   ```

3. **Create 15 new questions** following ground-truth methodology

4. **Create `dataset_expanded.json`** with all 25 questions

5. **Run evaluation experiments**
   ```bash
   python evaluation/run_evaluation.py --mode dense --dataset dataset_expanded.json
   python evaluation/run_evaluation.py --mode hybrid --dataset dataset_expanded.json
   python evaluation/run_evaluation.py --mode hybrid --rrf-alpha 1.2 --rrf-beta 0.8 --dataset dataset_expanded.json
   python evaluation/run_evaluation.py --mode hybrid --rrf-alpha 1.4 --rrf-beta 0.6 --dataset dataset_expanded.json
   python evaluation/run_evaluation.py --mode hybrid --rrf-alpha 1.6 --rrf-beta 0.4 --dataset dataset_expanded.json
   ```

6. **Analyze results** and create `PHASE9A_IMPLEMENTATION_REPORT.md`

7. **Commit Phase 9a**:
   ```
   feat(phase9a): expand benchmark to 25 questions for within-paper validation
   ```

### Future Actions (Phase 9b)

1. **Identify candidate papers** (4-9 additional papers)
2. **Acquire and process papers**
3. **Create 40-50 cross-paper questions**
4. **Run multi-paper evaluation**
5. **Analyze cross-paper generalization**
6. **Make production recommendation**

---

## Audit Complete

**Date**: 2026-10-06  
**Status**: AUDIT ONLY - NO IMPLEMENTATION  
**Recommendation**: PROCEED WITH PHASE 9A (25-QUESTION SINGLE-PAPER EXPANSION)

**Key Finding**: Database contains only 1 unique paper, limiting immediate multi-paper expansion. Two-phase approach recommended: Phase 9a (25 questions, 1 paper) immediately, Phase 9b (50-60 questions, 5-10 papers) after corpus acquisition.
