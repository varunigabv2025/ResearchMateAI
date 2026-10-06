"""
Quick summary of Phase 8 weighted RRF results.
"""
import json

configs = [
    ("C0 (α=1.0, β=1.0)", "evaluation/results/phase8_rrf_control_1_0.json"),
    ("W1 (α=1.2, β=0.8)", "evaluation/results/phase8_rrf_weighted_1_2_0_8.json"),
    ("W2 (α=1.4, β=0.6)", "evaluation/results/phase8_rrf_weighted_1_4_0_6.json"),
    ("W3 (α=1.6, β=0.4)", "evaluation/results/phase8_rrf_weighted_1_6_0_4.json"),
]

print("\n" + "="*80)
print("PHASE 8 WEIGHTED RRF RESULTS SUMMARY")
print("="*80)
print(f"{'Config':<20} | Recall@10 | MRR   | Hit@5 | Latency(ms)")
print("-"*80)

for name, path in configs:
    with open(path) as f:
        r = json.load(f)
        recall10 = r['retrieval_metrics']['recall_at_10']
        mrr = r['retrieval_metrics']['mrr']
        hit5 = r['retrieval_metrics']['hit_rate_at_5']
        latency = r['latency_metrics']['retrieval']['mean'] * 1000
        
        print(f"{name:<20} | {recall10:.3f}     | {mrr:.3f} | {hit5:.3f} | {latency:.1f}")

print("="*80)
