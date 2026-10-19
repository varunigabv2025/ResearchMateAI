# Phase 9B-1: Research Paper Acquisition Planning

**Planning Date**: 2026-10-09  
**Mode**: PLANNING ONLY - NO DOWNLOADS OR INGESTION  
**Objective**: Identify 6 additional open-access research papers for multi-paper benchmark

---

## Executive Summary

This document identifies 6 candidate open-access research papers from diverse AI/ML technical domains to complement the existing PA-EIS paper. All candidates are verified from arXiv with confirmed PDF availability, distinct technical domains, and substantial research content suitable for RAG evaluation.

**Recommended Papers**:
1. Deep Residual Learning (ResNet) - **Computer Vision**
2. BERT Pre-training - **Natural Language Processing**
3. Attention Is All You Need (Transformer) - **NLP / Architecture**
4. YOLO Object Detection - **Computer Vision**
5. MobileNets - **Model Compression / Edge Computing**
6. Pruning and Quantization Survey - **Model Compression**

**Domain Coverage**: 4 distinct domains (NLP, Computer Vision, Model Compression, Edge Computing)  
**Total Corpus**: 7 papers (1 existing + 6 new)

---

## 1. Existing Paper Inventory

### Paper 1: PA-EIS IEEE (Already Ingested)

| Field | Value |
|-------|-------|
| **Full Title** | Priority-Aware Operating System Scheduling for Concurrent Edge AI Inference Workloads: An Empirical Study |
| **Domain** | Edge Computing / Operating Systems |
| **Page Count** | 6 pages |
| **Chunk Count** | 54 chunks |
| **Status** | ✓ Ingested and validated |
| **Phase 9A Questions** | 25 questions (proven suitable) |
| **Suitability** | **SUITABLE** - Proven in Phase 9A |

**Assessment**: PA-EIS is a high-quality edge computing paper with proven suitability for RAG evaluation. It has clear methodology, experimental design, and meaningful metrics. Serves as excellent baseline for domain diversity comparison.

---

## 2. Candidate Paper Selection Criteria

### Required Criteria

✓ **Open access**: arXiv or open journal/conference  
✓ **PDF availability**: Confirmed downloadable PDF  
✓ **Text layer**: Not scanned images (verified via arXiv)  
✓ **Length**: 4-20 pages (conference/journal papers)  
✓ **Domain**: Distinct from existing papers  
✓ **Original research**: Not surveys only (methodology + results)  
✓ **English language**: Full paper in English  
✓ **License**: Research use permitted (arXiv policy)

### Quality Criteria

✓ **Methodology section**: Clear experimental or theoretical approach  
✓ **Results section**: Reported metrics, experiments, or proofs  
✓ **Numerical content**: Metrics, statistics, or quantitative results  
✓ **Limitations stated**: Authors discuss constraints or future work  
✓ **Sufficient text**: Enough content for 5-10 diverse questions  
✓ **Well-structured**: Clear sections (Introduction, Methods, Results, etc.)

---

## 3. Candidate Papers (6 Additional Papers)

### Candidate 1: Deep Residual Learning for Image Recognition (ResNet)

| Field | Value |
|-------|-------|
| **Title** | Deep Residual Learning for Image Recognition |
| **Authors** | Kaiming He, Xiangyu Zhang, Shaoqing Ren, Jian Sun |
| **Domain** | **Computer Vision** - Convolutional Neural Networks |
| **Publication** | CVPR 2016 (also arXiv:1512.03385) |
| **arXiv ID** | 1512.03385 |
| **PDF URL** | https://arxiv.org/pdf/1512.03385.pdf |
| **Abstract URL** | https://arxiv.org/abs/1512.03385 |
| **Submission Date** | December 10, 2015 |
| **Page Count** | 12 pages (estimated from arXiv metadata) |
| **License** | arXiv.org perpetual license |

**Abstract Summary** (content rephrased for compliance):
The paper presents a residual learning framework that simplifies training of very deep neural networks. Networks with up to 152 layers are evaluated, achieving improved accuracy on ImageNet and winning ILSVRC 2015. The residual connections allow gradients to flow through shortcut paths, enabling training of substantially deeper architectures than previously possible.

**Key Contributions**:
- Residual learning framework (skip connections)
- 152-layer network evaluation
- ImageNet top-5 error: 3.57%
- ILSVRC 2015 1st place
- Analysis on CIFAR-10 with 100 and 1000 layers
- COCO detection improvements

**Suitability Assessment**: **SUITABLE**

**Rationale**:
- ✓ Clear methodology (residual blocks, shortcut connections)
- ✓ Extensive experimental results (ImageNet, CIFAR-10, COCO)
- ✓ Numerical metrics (error rates, layer depths)
- ✓ Architectural innovations (skip connections)
- ✓ Multiple datasets and tasks
- ✓ Distinct from edge computing domain
- ✓ Well-structured paper with clear sections

**Question Potential**:
- Factual: "What is a residual block?"
- Methodological: "How do residual connections enable deep network training?"
- Numerical: "What accuracy did ResNet-152 achieve on ImageNet?"
- Conceptual: "Why do very deep networks suffer from degradation?"
- Multi-chunk: "How does ResNet compare to VGG on ImageNet and COCO?"

**PDF Verified**: ✓ Yes (arXiv PDF available)  
**Text Layer**: ✓ Yes (arXiv standard)  
**Provisionally Suitable**: **YES** (PDF inspection recommended)

---

### Candidate 2: BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding

| Field | Value |
|-------|-------|
| **Title** | BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding |
| **Authors** | Jacob Devlin, Ming-Wei Chang, Kenton Lee, Kristina Toutanova |
| **Domain** | **Natural Language Processing** - Language Models |
| **Publication** | NAACL 2019 (also arXiv:1810.04805) |
| **arXiv ID** | 1810.04805 |
| **PDF URL** | https://arxiv.org/pdf/1810.04805.pdf |
| **Abstract URL** | https://arxiv.org/abs/1810.04805 |
| **Submission Date** | October 11, 2018 |
| **Page Count** | 16 pages (estimated from arXiv metadata) |
| **License** | arXiv.org perpetual license |

**Abstract Summary** (content rephrased for compliance):
BERT introduces bidirectional pre-training for language representations using Transformers. Unlike prior approaches, BERT conditions on both left and right context jointly in all layers. The pre-trained model can be fine-tuned with a single output layer for various NLP tasks. BERT achieves state-of-the-art on eleven NLP benchmarks, including significant improvements on GLUE, MultiNLI, and SQuAD.

**Key Contributions**:
- Bidirectional pre-training approach
- Masked language modeling objective
- Next sentence prediction task
- GLUE score: 80.5% (+7.7 points)
- MultiNLI accuracy: 86.7% (+4.6 points)
- SQuAD v1.1 F1: 93.2 (+1.5 points)
- SQuAD v2.0 F1: 83.1 (+5.1 points)

**Suitability Assessment**: **SUITABLE**

**Rationale**:
- ✓ Clear pre-training methodology
- ✓ Multiple benchmark results
- ✓ Numerical performance metrics
- ✓ Novel training objectives (MLM, NSP)
- ✓ Distinct NLP domain
- ✓ Fine-tuning approach documented
- ✓ Ablation studies included

**Question Potential**:
- Factual: "What does BERT stand for?"
- Methodological: "How does masked language modeling work?"
- Numerical: "What GLUE score did BERT achieve?"
- Conceptual: "How is BERT different from GPT?"
- Multi-chunk: "What pre-training tasks does BERT use?"

**PDF Verified**: ✓ Yes (arXiv PDF available)  
**Text Layer**: ✓ Yes (arXiv standard)  
**Provisionally Suitable**: **YES** (PDF inspection recommended)

---

### Candidate 3: Attention Is All You Need (Transformer)

| Field | Value |
|-------|-------|
| **Title** | Attention Is All You Need |
| **Authors** | Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Łukasz Kaiser, Illia Polosukhin |
| **Domain** | **NLP / Neural Architecture** - Machine Translation |
| **Publication** | NeurIPS 2017 (also arXiv:1706.03762) |
| **arXiv ID** | 1706.03762 |
| **PDF URL** | https://arxiv.org/pdf/1706.03762.pdf |
| **Abstract URL** | https://arxiv.org/abs/1706.03762 |
| **Submission Date** | June 12, 2017 |
| **Page Count** | 15 pages |
| **License** | arXiv.org perpetual license |

**Abstract Summary** (content rephrased for compliance):
The Transformer architecture is proposed as a novel network based solely on attention mechanisms, without recurrence or convolutions. Experiments on machine translation show superior quality with better parallelization and reduced training time. The model achieves 28.4 BLEU on WMT 2014 English-German and 41.8 BLEU on English-French, establishing new state-of-the-art results. The architecture generalizes well to English constituency parsing.

**Key Contributions**:
- Transformer architecture (self-attention only)
- Multi-head attention mechanism
- Positional encoding
- WMT 2014 En-De: 28.4 BLEU (+2.0 improvement)
- WMT 2014 En-Fr: 41.8 BLEU (new SOTA)
- Parallel training efficiency
- English constituency parsing results

**Suitability Assessment**: **SUITABLE**

**Rationale**:
- ✓ Novel architecture design
- ✓ Clear methodology (attention layers, positional encoding)
- ✓ Multiple translation tasks
- ✓ Numerical BLEU scores
- ✓ Training efficiency comparisons
- ✓ Foundational NLP paper
- ✓ Architectural diagrams and explanations

**Question Potential**:
- Factual: "What is the Transformer architecture?"
- Methodological: "How does multi-head attention work?"
- Numerical: "What BLEU score did the Transformer achieve on WMT 2014 En-De?"
- Conceptual: "Why does the Transformer not use recurrence?"
- Multi-chunk: "How does positional encoding work in Transformers?"

**PDF Verified**: ✓ Yes (arXiv PDF available)  
**Text Layer**: ✓ Yes (arXiv standard)  
**Provisionally Suitable**: **YES** (PDF inspection recommended)

---

### Candidate 4: You Only Look Once: Unified, Real-Time Object Detection (YOLO)

| Field | Value |
|-------|-------|
| **Title** | You Only Look Once: Unified, Real-Time Object Detection |
| **Authors** | Joseph Redmon, Santosh Divvala, Ross Girshick, Ali Farhadi |
| **Domain** | **Computer Vision** - Object Detection |
| **Publication** | CVPR 2016 (also arXiv:1506.02640) |
| **arXiv ID** | 1506.02640 |
| **PDF URL** | https://arxiv.org/pdf/1506.02640.pdf |
| **Abstract URL** | https://arxiv.org/abs/1506.02640 |
| **Submission Date** | June 8, 2015 |
| **Page Count** | 10 pages (estimated from arXiv metadata) |
| **License** | arXiv.org perpetual license |

**Abstract Summary** (content rephrased for compliance):
YOLO frames object detection as a regression problem rather than classifier-based detection. A single neural network predicts bounding boxes and class probabilities directly from full images in one pass. The base model processes images at 45 frames per second, with a faster variant achieving 155 FPS. YOLO makes fewer false positives than other detectors and learns general object representations that transfer well to artwork domains.

**Key Contributions**:
- Single-pass object detection
- Real-time processing (45-155 FPS)
- Unified architecture (end-to-end training)
- Spatial regression of bounding boxes
- Generalization to artwork (Picasso, People-Art datasets)
- Trade-off: localization errors vs. false positives

**Suitability Assessment**: **SUITABLE**

**Rationale**:
- ✓ Novel detection paradigm
- ✓ Clear methodology (grid-based prediction)
- ✓ Speed and accuracy metrics
- ✓ Multiple datasets (PASCAL VOC, artwork)
- ✓ Distinct computer vision approach
- ✓ Real-time performance focus
- ✓ Comparative analysis with R-CNN, DPM

**Question Potential**:
- Factual: "What does YOLO stand for?"
- Methodological: "How does YOLO predict bounding boxes?"
- Numerical: "What frame rate does YOLO achieve?"
- Conceptual: "Why is YOLO faster than R-CNN?"
- Multi-chunk: "What are the trade-offs of YOLO's approach?"

**PDF Verified**: ✓ Yes (arXiv PDF available)  
**Text Layer**: ✓ Yes (arXiv standard)  
**Provisionally Suitable**: **YES** (PDF inspection recommended)

---

### Candidate 5: MobileNets: Efficient Convolutional Neural Networks for Mobile Vision Applications

| Field | Value |
|-------|-------|
| **Title** | MobileNets: Efficient Convolutional Neural Networks for Mobile Vision Applications |
| **Authors** | Andrew G. Howard, Menglong Zhu, Bo Chen, Dmitry Kalenichenko, Weijun Wang, Tobias Weyand, Marco Andreetto, Hartwig Adam |
| **Domain** | **Model Compression / Edge Computing** - Efficient Neural Networks |
| **Publication** | arXiv:1704.04861 (2017) |
| **arXiv ID** | 1704.04861 |
| **PDF URL** | https://arxiv.org/pdf/1704.04861.pdf |
| **Abstract URL** | https://arxiv.org/abs/1704.04861 |
| **Submission Date** | April 17, 2017 |
| **Page Count** | 9 pages (estimated) |
| **License** | arXiv.org perpetual license |

**Abstract Summary** (content rephrased for compliance):
MobileNets are efficient models designed for mobile and embedded vision. The architecture uses depthwise separable convolutions to reduce computation and model size. Two hyperparameters (width multiplier and resolution multiplier) allow trading off latency and accuracy. Experiments demonstrate strong ImageNet performance with efficiency improvements. Applications include object detection, fine-grained classification, face attributes, and geo-localization.

**Key Contributions**:
- Depthwise separable convolutions
- Width and resolution multipliers
- Mobile-optimized architecture
- ImageNet classification results
- Multi-task applications
- Latency vs. accuracy trade-offs

**Suitability Assessment**: **SUITABLE**

**Rationale**:
- ✓ Model compression techniques
- ✓ Clear architectural design
- ✓ Efficiency metrics (latency, size)
- ✓ ImageNet benchmarks
- ✓ Bridges edge computing and compression
- ✓ Multiple downstream tasks
- ✓ Hyperparameter analysis

**Question Potential**:
- Factual: "What are depthwise separable convolutions?"
- Methodological: "How do width multipliers affect MobileNet?"
- Numerical: "What is the computation reduction of MobileNet?"
- Conceptual: "Why are MobileNets suitable for mobile devices?"
- Multi-chunk: "What applications are demonstrated with MobileNets?"

**PDF Verified**: ✓ Yes (arXiv PDF available)  
**Text Layer**: ✓ Yes (arXiv standard)  
**Provisionally Suitable**: **YES** (PDF inspection recommended)

---

### Candidate 6: Pruning and Quantization for Deep Neural Network Acceleration: A Survey

| Field | Value |
|-------|-------|
| **Title** | Pruning and Quantization for Deep Neural Network Acceleration: A Survey |
| **Authors** | Tailin Liang, John Glossner, Lei Wang, Shaobo Shi, Xiaotong Zhang |
| **Domain** | **Model Compression** - Pruning and Quantization |
| **Publication** | arXiv:2101.09671 (2021) |
| **arXiv ID** | 2101.09671 |
| **PDF URL** | https://arxiv.org/pdf/2101.09671.pdf |
| **Abstract URL** | https://arxiv.org/abs/2101.09671 |
| **Submission Date** | January 24, 2021 |
| **Page Count** | 36 pages (survey paper) |
| **License** | arXiv.org perpetual license |

**Abstract Summary** (content rephrased for compliance):
The survey covers two primary network compression techniques: pruning and quantization. Pruning is categorized as static (offline) or dynamic (runtime). Various pruning granularities are discussed: element-wise, channel-wise, filter-wise, layer-wise, and network-wise. Quantization reduces computation by lowering precision, typically to 8-bit integers or even binary. The survey compares techniques, analyzes trade-offs, presents accuracy results across frameworks, and provides practical compression guidance.

**Key Contributions**:
- Comprehensive pruning taxonomy
- Quantization methods (8-bit, binary, etc.)
- Static vs. dynamic pruning
- Granularity trade-offs
- Accuracy preservation techniques
- Combined pruning + quantization
- Practical deployment guidance

**Suitability Assessment**: **PARTIALLY SUITABLE** (Survey paper - use cautiously)

**Rationale**:
- ✓ Comprehensive methodology coverage
- ✓ Taxonomy and categorization
- ✓ Comparison of techniques
- ✓ Practical guidance included
- ⚠️ Survey paper (less original methodology)
- ⚠️ 36 pages (longer than typical papers)
- ✓ Distinct compression domain
- ✓ Numerical comparisons across methods

**Question Potential**:
- Factual: "What is network pruning?"
- Methodological: "What is the difference between static and dynamic pruning?"
- Numerical: "What precision levels are used in quantization?"
- Conceptual: "Why does pruning not always reduce accuracy?"
- Multi-chunk: "How do pruning and quantization compare?"

**Caveat**: Survey papers may have different structure than research papers. Questions should focus on taxonomy, methodology comparison, and synthesis rather than single-experiment results.

**PDF Verified**: ✓ Yes (arXiv PDF available)  
**Text Layer**: ✓ Yes (arXiv standard)  
**Provisionally Suitable**: **YES** (but verify question types suit survey format)

---

## 4. Domain Distribution Analysis

### Target Domains (From Phase 9B Audit)

| Domain | Papers | Coverage |
|--------|--------|----------|
| **Edge Computing / Systems** | PA-EIS, MobileNets | 2 papers |
| **Computer Vision** | ResNet, YOLO | 2 papers |
| **Natural Language Processing** | BERT, Transformer | 2 papers |
| **Model Compression** | MobileNets, Pruning Survey | 2 papers |

**Total**: 7 papers across 4 distinct domains

### Domain Overlap Analysis

**Minimal Overlap**:
- PA-EIS (OS scheduling) vs. MobileNets (efficient CNNs): Different subfields within edge computing
- ResNet (image classification) vs. YOLO (object detection): Different CV tasks
- BERT (language understanding) vs. Transformer (translation): Different NLP tasks
- MobileNets (architecture) vs. Pruning Survey (compression techniques): Different compression approaches

**Terminology Diversity**:
- Edge: cgroups, CFS, scheduling, containers
- CV: residual blocks, bounding boxes, convolutional layers
- NLP: transformers, attention, BLEU, masked language modeling
- Compression: pruning, quantization, depthwise separable

**Assessment**: Strong domain diversity with minimal terminology overlap. Should reduce cross-paper retrieval contamination risk.

---

## 5. Paper Length and Chunk Estimates

| Paper | Est. Pages | Est. Chunks (1000 char/chunk) | Question Target |
|-------|------------|-------------------------------|-----------------|
| PA-EIS | 6 pages | 54 chunks | 25 questions (Phase 9A) |
| ResNet | 12 pages | ~100 chunks | 8-10 questions |
| BERT | 16 pages | ~140 chunks | 8-10 questions |
| Transformer | 15 pages | ~130 chunks | 8-10 questions |
| YOLO | 10 pages | ~85 chunks | 6-8 questions |
| MobileNets | 9 pages | ~75 chunks | 6-8 questions |
| Pruning Survey | 36 pages | ~300 chunks | 6-8 questions |

**Total Estimated Chunks**: ~884 chunks (7 papers)  
**Total Question Target**: 53-62 questions (7.5-8.9 per paper)

**Note**: Chunk estimates are approximate. Actual counts will vary based on text density, figures, equations, and references.

---

## 6. Verification Status

### Papers with Verified Metadata

| Paper | arXiv ID | PDF URL Verified | Abstract Verified | License |
|-------|----------|------------------|-------------------|---------|
| PA-EIS | N/A (IEEE) | ✓ Ingested | ✓ Ingested | IEEE |
| ResNet | 1512.03385 | ✓ Yes | ✓ Yes | arXiv |
| BERT | 1810.04805 | ✓ Yes | ✓ Yes | arXiv |
| Transformer | 1706.03762 | ✓ Yes | ✓ Yes | arXiv |
| YOLO | 1506.02640 | ✓ Yes | ✓ Yes | arXiv |
| MobileNets | 1704.04861 | ✓ Yes | ✓ Yes | arXiv |
| Pruning Survey | 2101.09671 | ✓ Yes | ✓ Yes | arXiv |

**All candidate papers verified** via arXiv abstract pages. PDF URLs are standard arXiv format and confirmed accessible.

### Items NOT Yet Verified

⚠️ **PDF text layer quality**: Assumed present (arXiv standard) but not manually inspected  
⚠️ **Exact page count**: Estimated from arXiv metadata, not from PDF inspection  
⚠️ **Section structure**: Not verified (Introduction, Methods, Results assumed)  
⚠️ **Figure/table density**: Unknown (affects chunk count and question types)  
⚠️ **Reference section length**: Unknown (may be excluded from chunking)

**Recommendation**: Download and manually inspect PDFs before ingestion to verify:
1. Text layer extractable (not scanned)
2. Sufficient textual content (not mostly figures/tables)
3. Clear section structure
4. Readable formatting

---

## 7. Alternative Candidates Considered

### Not Selected

| Paper | Domain | Reason Not Selected |
|-------|--------|---------------------|
| DQN (Deep Q-Learning) | Reinforcement Learning | Good candidate but prioritized other domains for balance |
| Improved ResNets (2004.04989) | Computer Vision | Too similar to original ResNet |
| MobileNetV4 (2404.10518) | Model Compression | Too similar to original MobileNet |
| Fine-Grained Attention NMT | NLP | Less impactful than Transformer/BERT |
| DistilBERT | NLP/Compression | Too dependent on BERT (derivative work) |

**Rationale**: Prioritized foundational, high-impact papers with distinct contributions. Avoided derivative works that depend heavily on understanding a parent paper (e.g., DistilBERT requires BERT knowledge).

---

## 8. Risk Assessment

### Risk 1: Survey Paper (Pruning & Quantization)

**Issue**: Survey papers have different structure than research papers  
**Mitigation**: Focus questions on taxonomy, method comparison, and synthesis  
**Fallback**: Replace with a research paper if question creation proves difficult

**Alternative**: "Learning Efficient Convolutional Networks through Network Slimming" (arXiv:1708.06519) - original research on structured pruning

### Risk 2: Paper Similarity

**Issue**: MobileNets and PA-EIS both relate to edge deployment  
**Mitigation**: Distinct focus (architecture design vs. OS scheduling)  
**Evidence**: Different terminology (depthwise convolutions vs. cgroups)

### Risk 3: PDF Text Extraction

**Issue**: Some papers may have poor text layer or equations  
**Mitigation**: Manual PDF inspection before ingestion  
**Verification**: Download and test extraction with PDFExtractor service

### Risk 4: Chunk Count Estimates

**Issue**: Actual chunk counts may differ significantly  
**Mitigation**: Verify after ingestion, adjust question allocation  
**Impact**: Low (questions allocated by content richness, not fixed per paper)

---

## 9. Duplicate Detection Strategy

### Content Hash Verification

After ingestion, verify no duplicate papers using:
1. MD5 hash of all chunk texts (Phase 9B audit method)
2. Title comparison (exact match)
3. Author comparison (common author subset)
4. Page count comparison (identical page count suspicious)

### Expected Unique Papers

All 6 candidates have:
- ✓ Distinct titles
- ✓ Distinct author sets (no common authors across all)
- ✓ Different publication years
- ✓ Different arXiv IDs

**Conclusion**: No duplicates expected among candidates.

---

## 10. License and Legal Verification

### arXiv Perpetual License

All 6 candidate papers are from arXiv, which grants:
- Perpetual, non-exclusive license to distribute
- Permission for research and educational use
- No copyright transfer (authors retain rights)
- Attribution required

**Source**: [arXiv License Information](https://arxiv.org/help/license)

### Research Use Compliance

**Phase 9B use case**: RAG retrieval benchmark evaluation

**Permitted under arXiv license**:
- ✓ Downloading PDFs
- ✓ Text extraction for research
- ✓ Chunking and embedding
- ✓ Question-answering evaluation
- ✓ Non-commercial research

**Not permitted**:
- ✗ Commercial deployment without verification
- ✗ Redistribution of modified PDFs
- ✗ Removal of author attribution

**Compliance**: Phase 9B is fully compliant with arXiv research use.

---

## 11. Recommended Paper Selection

### Final Selection (6 Papers)

| # | Paper | Domain | Priority | Rationale |
|---|-------|--------|----------|-----------|
| 1 | **ResNet** | Computer Vision | **HIGH** | Foundational CV paper, clear methodology, extensive results |
| 2 | **BERT** | NLP | **HIGH** | Foundational NLP paper, bidirectional pre-training, multiple benchmarks |
| 3 | **Transformer** | NLP / Architecture | **HIGH** | Introduced attention mechanism, machine translation results |
| 4 | **YOLO** | Computer Vision | **HIGH** | Real-time object detection, distinct from ResNet classification |
| 5 | **MobileNets** | Model Compression | **MEDIUM** | Efficient architectures, edge deployment, complements PA-EIS |
| 6 | **Pruning Survey** | Model Compression | **MEDIUM** | Compression taxonomy, method comparison (survey structure risk) |

**Confidence**: **HIGH** (5/6 papers)  
**Medium Confidence**: Pruning Survey (survey format may affect question types)

### Fallback Option

If Pruning Survey proves unsuitable (after PDF inspection):

**Replace with**: "Learning Efficient Convolutional Networks through Network Slimming" (arXiv:1708.06519)
- Original pruning research paper
- Channel-level sparsity
- Clear methodology and experiments
- ImageNet and CIFAR results

---

## 12. Next Steps: Paper Acquisition Procedure

### Step 1: Download PDFs

**For each paper**:
1. Navigate to arXiv PDF URL (listed in Section 3)
2. Download PDF to local storage
3. Verify file size (should be 500KB - 5MB typically)
4. Verify filename matches arXiv ID

**Recommended directory**: `ResearchAI/papers/phase9b/`

**Example**:
```bash
mkdir -p papers/phase9b
cd papers/phase9b
wget https://arxiv.org/pdf/1512.03385.pdf -O resnet_1512.03385.pdf
wget https://arxiv.org/pdf/1810.04805.pdf -O bert_1810.04805.pdf
wget https://arxiv.org/pdf/1706.03762.pdf -O transformer_1706.03762.pdf
wget https://arxiv.org/pdf/1506.02640.pdf -O yolo_1506.02640.pdf
wget https://arxiv.org/pdf/1704.04861.pdf -O mobilenets_1704.04861.pdf
wget https://arxiv.org/pdf/2101.09671.pdf -O pruning_survey_2101.09671.pdf
```

### Step 2: Manual PDF Inspection

**For each downloaded PDF, verify**:
1. ✓ Opens correctly in PDF viewer
2. ✓ Text is selectable (not scanned image)
3. ✓ Sections are identifiable (Introduction, Methods, Results, Conclusion)
4. ✓ Figures/tables do not dominate (< 50% of content)
5. ✓ References section is present (exclude from chunking if desired)
6. ✓ Page count matches estimate

**Rejection criteria**:
- ✗ Text not selectable (scanned PDF)
- ✗ Mostly figures/tables (< 3 pages substantive text)
- ✗ Garbled text extraction
- ✗ Missing critical sections

### Step 3: Test Text Extraction

**Using existing PDFExtractor service**:
```python
from app.services import PDFExtractor

# Test extraction on one paper
pdf_path = "papers/phase9b/resnet_1512.03385.pdf"
is_valid, error_msg = PDFExtractor.validate_pdf(pdf_path)
print(f"Valid: {is_valid}, Error: {error_msg}")

pages_data = PDFExtractor.extract_text_with_pages(pdf_path)
print(f"Extracted {len(pages_data)} pages")
print(f"First page preview: {pages_data[0]['text'][:200]}...")
```

**Expected output**: Clean text extraction with page numbers, no encoding errors.

### Step 4: Document Inspection Results

**Create**: `PHASE9B_PDF_INSPECTION_LOG.md`

**Template for each paper**:
```markdown
## Paper: [Title]
- PDF Downloaded: [Yes/No]
- Text Selectable: [Yes/No]
- Pages Extracted: [Count]
- Section Structure: [Clear/Unclear]
- Text Quality: [Good/Fair/Poor]
- Figures/Tables: [Percentage estimate]
- **Verdict**: [SUITABLE / UNSUITABLE]
- **Notes**: [Any issues or observations]
```

### Step 5: Decision Point

**If all 6 papers pass inspection**: Proceed to Phase 9B-2 (ingestion)  
**If 1-2 papers fail inspection**: Use fallback alternatives from Section 11  
**If 3+ papers fail inspection**: Re-evaluate paper selection strategy

---

## 13. Success Criteria for Phase 9B-1

Phase 9B-1 (Paper Acquisition Planning) is complete when:

- [✓] 6 candidate papers identified
- [✓] All candidates verified on arXiv (PDF URLs confirmed)
- [✓] Domain distribution analyzed (4 domains minimum)
- [✓] Paper metadata documented (title, authors, publication, domain)
- [✓] Abstract summaries created (rephrased for compliance)
- [✓] Suitability assessed (SUITABLE / PARTIALLY SUITABLE)
- [✓] Risk assessment documented
- [✓] License compliance verified
- [✓] Next steps documented (download, inspect, test extraction)
- [ ] **PENDING**: PDF downloads (not performed in planning phase)
- [ ] **PENDING**: Manual PDF inspection (not performed in planning phase)
- [ ] **PENDING**: Text extraction testing (not performed in planning phase)

**Current Status**: Planning phase complete, awaiting user approval to proceed with PDF acquisition.

---

## 14. Limitations and Assumptions

### Assumptions

1. **Text layer present**: Assumed all arXiv PDFs have extractable text (standard for arXiv)
2. **Page count accurate**: Estimated from arXiv metadata, not verified from PDFs
3. **Section structure**: Assumed standard research paper structure (may vary)
4. **Chunk estimates**: Rough estimates based on page count (actual may differ)
5. **Question suitability**: Based on abstract review, not full paper inspection

### Known Limitations

1. **No PDF downloads**: PDFs not yet obtained (planning phase only)
2. **No text extraction testing**: Cannot verify text quality until PDF acquired
3. **No section detection testing**: Section names may vary from expected
4. **Survey paper risk**: Pruning Survey may have different structure than research papers
5. **Single reviewer**: Paper selection by single evaluator (no peer review)

### Mitigation Strategy

- Download and inspect PDFs before ingestion (Step 2)
- Test text extraction on sample papers (Step 3)
- Document inspection results (Step 4)
- Use fallback alternatives if papers unsuitable (Section 11)

---

## 15. Git Status

**Mode**: Planning only - no files modified

**Files created**:
- `PHASE9B_PAPER_SELECTION.md` (this document)

**Files NOT created**:
- No PDFs downloaded
- No papers ingested
- No database modifications
- No code changes

**Branch**: main  
**HEAD**: 03434efee6392fb69b6348496df044af5ed56096 (unchanged)  
**Status**: Clean (planning document untracked)

---

## 16. Summary and Recommendations

### Papers Recommended for Phase 9B

| # | Paper | arXiv ID | Domain | Confidence |
|---|-------|----------|--------|------------|
| 1 | Deep Residual Learning (ResNet) | 1512.03385 | Computer Vision | **HIGH** |
| 2 | BERT Pre-training | 1810.04805 | NLP | **HIGH** |
| 3 | Attention Is All You Need | 1706.03762 | NLP / Architecture | **HIGH** |
| 4 | YOLO Object Detection | 1506.02640 | Computer Vision | **HIGH** |
| 5 | MobileNets | 1704.04861 | Model Compression | **MEDIUM** |
| 6 | Pruning & Quantization Survey | 2101.09671 | Model Compression | **MEDIUM** |

### Domain Coverage

- **Computer Vision**: 2 papers (ResNet, YOLO)
- **Natural Language Processing**: 2 papers (BERT, Transformer)
- **Model Compression**: 2 papers (MobileNets, Pruning Survey)
- **Edge Computing**: 1 paper (PA-EIS - existing)

**Total**: 7 papers, 4 domains ✓ Exceeds 3-domain minimum

### Next Action

**Recommended**: Proceed to **PDF Acquisition and Inspection**

**Steps**:
1. Download 6 PDFs from arXiv
2. Manually inspect each PDF (text layer, structure, quality)
3. Test text extraction with PDFExtractor
4. Document inspection results
5. If all pass: Proceed to Phase 9B-2 (Ingestion)
6. If any fail: Use fallback alternatives

**Estimated Time**: 1-2 hours (download + inspection)

---

**END OF PHASE 9B-1: PAPER ACQUISITION PLANNING**

