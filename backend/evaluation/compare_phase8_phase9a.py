"""Compare Phase 8 vs Phase 9A results."""
import json

# Load Phase 8 results
p8_control = json.load(open('backend/evaluation/results/phase8_rrf_control_1_0.json'))
p8_w1 = json.load(open('backend/evaluation/results/phase8_rrf_weighted_1_2_0_8.json'))

# Load Phase 9A results
p9a_hybrid = json.load(open('backend/evaluation/results/phase9a_hybrid.json'))
p9a_w1 = json.load(open('backend/evaluation/results/phase9a_rrf_weighted_1_2_0_8.json'))

print("="*80)
print("PHASE 8 vs PHASE 9A COMPARISON")
print("="*80)

print("\nPhase 8 (10 questions):")
print(f"  Hybrid (α=1.0, β=1.0): R@10={p8_control['retrieval_metrics']['recall_at_10']:.3f}, MRR={p8_control['retrieval_metrics']['mrr']:.3f}")
print(f"  W1 (α=1.2, β=0.8):      R@10={p8_w1['retrieval_metrics']['recall_at_10']:.3f}, MRR={p8_w1['retrieval_metrics']['mrr']:.3f}")

p8_diff = p8_w1['retrieval_metrics']['recall_at_10'] - p8_control['retrieval_metrics']['recall_at_10']
print(f"  W1 vs Hybrid: {p8_diff*100:+.1f} percentage points")

print("\nPhase 9A (25 questions):")
print(f"  Hybrid (α=1.0, β=1.0): R@10={p9a_hybrid['retrieval_metrics']['recall_at_10']:.3f}, MRR={p9a_hybrid['retrieval_metrics']['mrr']:.3f}")
print(f"  W1 (α=1.2, β=0.8):      R@10={p9a_w1['retrieval_metrics']['recall_at_10']:.3f}, MRR={p9a_w1['retrieval_metrics']['mrr']:.3f}")

p9a_diff = p9a_w1['retrieval_metrics']['recall_at_10'] - p9a_hybrid['retrieval_metrics']['recall_at_10']
print(f"  W1 vs Hybrid: {p9a_diff*100:+.1f} percentage points")

print("\n" + "="*80)
print("INTERPRETATION")
print("="*80)
print(f"\nPhase 8:  Weighted RRF improved R@10 by {p8_diff*100:+.1f} pp")
print(f"Phase 9A: Weighted RRF changed R@10 by {p9a_diff*100:+.1f} pp")
print("\n⚠️  Results differed across benchmarks.")
print("This does NOT represent temporal improvement/regression.")
print("The weighted RRF effect is benchmark-dependent.")
