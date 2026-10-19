"""Quick summary of Phase 9A results."""
import json
from pathlib import Path

results_dir = Path(__file__).parent / 'results'
configs = [
    ('Dense', 'phase9a_dense.json'),
    ('Hybrid', 'phase9a_hybrid.json'),
    ('W1 (1.2/0.8)', 'phase9a_rrf_weighted_1_2_0_8.json'),
    ('W2 (1.4/0.6)', 'phase9a_rrf_weighted_1_4_0_6.json'),
    ('W3 (1.6/0.4)', 'phase9a_rrf_weighted_1_6_0_4.json'),
]

print('\nPHASE 9A RESULTS SUMMARY (25 questions)')
print('='*80)
print(f"{'Config':<15} | R@5   | R@10  | MRR   | Hit@5 | Latency")
print('-'*80)

for name, filename in configs:
    with open(results_dir / filename) as f:
        data = json.load(f)
    
    metrics = data['retrieval_metrics']
    latency = data['latency_metrics']['retrieval']['mean'] * 1000
    
    print(f"{name:<15} | {metrics['recall_at_5']:.3f} | {metrics['recall_at_10']:.3f} | {metrics['mrr']:.3f} | {metrics['hit_rate_at_5']:.3f} | {latency:.1f}ms")

print('='*80)
