"""
Generate Phase 6 comparison report between HYBRID and RERANKED modes.
"""
import json
from pathlib import Path


def load_results(filename):
    """Load evaluation results from JSON file."""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)


def compute_improvement(baseline_val, new_val):
    """Compute absolute and percentage improvement."""
    abs_improvement = new_val - baseline_val
    if baseline_val != 0:
        pct_improvement = (abs_improvement / baseline_val) * 100
    else:
        pct_improvement = 0 if new_val == 0 else float('inf')
    return abs_improvement, pct_improvement


def generate_comparison():
    """Generate comparison between hybrid and reranked modes."""
    
    # Load results
    hybrid_results = load_results('evaluation/results/phase6_hybrid_baseline.json')
    reranked_results = load_results('evaluation/results/phase6_reranked.json')
    
    # Extract metrics
    hybrid_metrics = hybrid_results['retrieval_metrics']
    reranked_metrics = reranked_results['retrieval_metrics']
    
    # Compute improvements
    comparison = {
        'phase': 'Phase 6: Cross-Encoder Reranking Evaluation',
        'timestamp': reranked_results['timestamp'],
        'paper': hybrid_results['paper'],
        'summary': {
            'hybrid_baseline': {
                'recall_at_5': hybrid_metrics['recall_at_5'],
                'mrr': hybrid_metrics['mrr'],
                'hit_rate_at_5': hybrid_metrics['hit_rate_at_5']
            },
            'reranked': {
                'recall_at_5': reranked_metrics['recall_at_5'],
                'mrr': reranked_metrics['mrr'],
                'hit_rate_at_5': reranked_metrics['hit_rate_at_5']
            }
        },
        'detailed_metrics': {}
    }
    
    # Add improvements
    for metric in ['hit_rate_at_1', 'hit_rate_at_3', 'hit_rate_at_5', 'hit_rate_at_10',
                   'recall_at_1', 'recall_at_3', 'recall_at_5', 'recall_at_10',
                   'precision_at_1', 'precision_at_3', 'precision_at_5', 'precision_at_10',
                   'mrr']:
        hybrid_val = hybrid_metrics[metric]
        reranked_val = reranked_metrics[metric]
        abs_imp, pct_imp = compute_improvement(hybrid_val, reranked_val)
        
        comparison['detailed_metrics'][metric] = {
            'hybrid': hybrid_val,
            'reranked': reranked_val,
            'absolute_improvement': abs_imp,
            'percent_improvement': pct_imp
        }
    
    # Add latency comparison
    comparison['latency_comparison'] = {
        'hybrid_retrieval_ms': hybrid_results['latency_metrics']['retrieval']['mean'] * 1000,
        'reranked_retrieval_ms': reranked_results['latency_metrics']['retrieval']['mean'] * 1000,
        'reranking_overhead_ms': (reranked_results['latency_metrics']['retrieval']['mean'] - 
                                   hybrid_results['latency_metrics']['retrieval']['mean']) * 1000
    }
    
    # Per-question analysis for difficult questions
    comparison['difficult_questions'] = {}
    
    for question in hybrid_results['per_question_results']:
        q_id = question['question_id']
        if q_id in ['q3', 'q4', 'q7', 'q8']:  # Known difficult questions
            # Find matching reranked question
            reranked_q = next((q for q in reranked_results['per_question_results'] if q['question_id'] == q_id), None)
            
            if reranked_q:
                comparison['difficult_questions'][q_id] = {
                    'question': question['question'][:80] + '...',
                    'hybrid': {
                        'recall_at_5': question['retrieval_metrics'].get('recall_at_5', 0),
                        'mrr': question['retrieval_metrics'].get('mrr', 0),
                        'retrieved_pages': question.get('retrieved_pages', [])[:5]
                    },
                    'reranked': {
                        'recall_at_5': reranked_q['retrieval_metrics'].get('recall_at_5', 0),
                        'mrr': reranked_q['retrieval_metrics'].get('mrr', 0),
                        'retrieved_pages': reranked_q.get('retrieved_pages', [])[:5]
                    }
                }
    
    # Key findings
    comparison['key_findings'] = [
        f"Reranked Recall@5: {reranked_metrics['recall_at_5']:.3f} vs Hybrid: {hybrid_metrics['recall_at_5']:.3f}",
        f"Reranked MRR: {reranked_metrics['mrr']:.3f} vs Hybrid: {hybrid_metrics['mrr']:.3f}",
        f"Reranking increased retrieval latency by {comparison['latency_comparison']['reranking_overhead_ms']:.1f}ms",
        f"Hit Rate@5: {reranked_metrics['hit_rate_at_5']:.3f} vs Hybrid: {hybrid_metrics['hit_rate_at_5']:.3f}"
    ]
    
    # Save comparison
    output_path = Path('evaluation/results/phase6_comparison.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)
    
    print(f"Comparison saved to: {output_path}")
    print("\n" + "="*60)
    print("PHASE 6: HYBRID vs RERANKED COMPARISON")
    print("="*60)
    print(f"\nRecall@5:")
    print(f"  Hybrid:    {hybrid_metrics['recall_at_5']:.3f}")
    print(f"  Reranked:  {reranked_metrics['recall_at_5']:.3f}")
    print(f"  Change:    {comparison['detailed_metrics']['recall_at_5']['absolute_improvement']:+.3f} ({comparison['detailed_metrics']['recall_at_5']['percent_improvement']:+.1f}%)")
    
    print(f"\nMRR:")
    print(f"  Hybrid:    {hybrid_metrics['mrr']:.3f}")
    print(f"  Reranked:  {reranked_metrics['mrr']:.3f}")
    print(f"  Change:    {comparison['detailed_metrics']['mrr']['absolute_improvement']:+.3f} ({comparison['detailed_metrics']['mrr']['percent_improvement']:+.1f}%)")
    
    print(f"\nHit Rate@5:")
    print(f"  Hybrid:    {hybrid_metrics['hit_rate_at_5']:.3f}")
    print(f"  Reranked:  {reranked_metrics['hit_rate_at_5']:.3f}")
    print(f"  Change:    {comparison['detailed_metrics']['hit_rate_at_5']['absolute_improvement']:+.3f} ({comparison['detailed_metrics']['hit_rate_at_5']['percent_improvement']:+.1f}%)")
    
    print(f"\nLatency:")
    print(f"  Hybrid retrieval:     {comparison['latency_comparison']['hybrid_retrieval_ms']:.1f}ms")
    print(f"  Reranked retrieval:   {comparison['latency_comparison']['reranked_retrieval_ms']:.1f}ms")
    print(f"  Reranking overhead:   {comparison['latency_comparison']['reranking_overhead_ms']:+.1f}ms")
    
    print("\n" + "="*60)


if __name__ == '__main__':
    generate_comparison()
