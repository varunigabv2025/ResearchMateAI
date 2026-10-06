"""
Phase 8 Final Verification Script

Extracts complete metrics from all four experimental configurations
and performs detailed per-question analysis.
"""
import json
from pathlib import Path

def load_results(path):
    """Load results JSON."""
    with open(path) as f:
        return json.load(f)

def print_complete_metrics():
    """Print complete metric table for all configurations."""
    configs = [
        ("C0 (α=1.0, β=1.0)", "evaluation/results/phase8_rrf_control_1_0.json"),
        ("W1 (α=1.2, β=0.8)", "evaluation/results/phase8_rrf_weighted_1_2_0_8.json"),
        ("W2 (α=1.4, β=0.6)", "evaluation/results/phase8_rrf_weighted_1_4_0_6.json"),
        ("W3 (α=1.6, β=0.4)", "evaluation/results/phase8_rrf_weighted_1_6_0_4.json"),
    ]
    
    print("\n" + "="*100)
    print("COMPLETE METRIC TABLE")
    print("="*100)
    print(f"{'Metric':<25} | {'C0 (1.0/1.0)':<12} | {'W1 (1.2/0.8)':<12} | {'W2 (1.4/0.6)':<12} | {'W3 (1.6/0.4)':<12}")
    print("-"*100)
    
    results = [load_results(path) for _, path in configs]
    
    metrics = [
        ('hit_rate_at_1', 'Hit Rate@1'),
        ('hit_rate_at_3', 'Hit Rate@3'),
        ('hit_rate_at_5', 'Hit Rate@5'),
        ('hit_rate_at_10', 'Hit Rate@10'),
        ('recall_at_1', 'Recall@1'),
        ('recall_at_3', 'Recall@3'),
        ('recall_at_5', 'Recall@5'),
        ('recall_at_10', 'Recall@10'),
        ('precision_at_1', 'Precision@1'),
        ('precision_at_3', 'Precision@3'),
        ('precision_at_5', 'Precision@5'),
        ('precision_at_10', 'Precision@10'),
        ('mrr', 'MRR'),
    ]
    
    for key, label in metrics:
        values = [r['retrieval_metrics'][key] for r in results]
        print(f"{label:<25} | {values[0]:<12.3f} | {values[1]:<12.3f} | {values[2]:<12.3f} | {values[3]:<12.3f}")
    
    # Latency
    latencies_mean = [r['latency_metrics']['retrieval']['mean'] * 1000 for r in results]
    latencies_std = [r['latency_metrics']['retrieval']['std_dev'] * 1000 for r in results]
    
    print(f"{'Latency mean (ms)':<25} | {latencies_mean[0]:<12.1f} | {latencies_mean[1]:<12.1f} | {latencies_mean[2]:<12.1f} | {latencies_mean[3]:<12.1f}")
    print(f"{'Latency std dev (ms)':<25} | {latencies_std[0]:<12.1f} | {latencies_std[1]:<12.1f} | {latencies_std[2]:<12.1f} | {latencies_std[3]:<12.1f}")
    print("="*100)

def analyze_per_question():
    """Analyze all 10 questions across configurations."""
    configs = [
        ("C0", "evaluation/results/phase8_rrf_control_1_0.json"),
        ("W1", "evaluation/results/phase8_rrf_weighted_1_2_0_8.json"),
        ("W2", "evaluation/results/phase8_rrf_weighted_1_4_0_6.json"),
        ("W3", "evaluation/results/phase8_rrf_weighted_1_6_0_4.json"),
    ]
    
    results = {name: load_results(path) for name, path in configs}
    
    print("\n" + "="*120)
    print("PER-QUESTION ANALYSIS (ALL 10 QUESTIONS)")
    print("="*120)
    
    # Get question count
    question_count = len(results['C0']['per_question_results'])
    
    for i in range(question_count):
        q_id = f"q{i+1}"
        print(f"\n{q_id.upper()}: {results['C0']['per_question_results'][i]['question'][:70]}...")
        print("-"*120)
        print(f"{'Config':<10} | {'Recall@5':<10} | {'Recall@10':<11} | {'MRR':<10} | {'Retrieved Pages':<50} | Change vs C0")
        print("-"*120)
        
        c0_recall5 = results['C0']['per_question_results'][i]['retrieval_metrics'].get('recall_at_5', 'N/A')
        c0_recall10 = results['C0']['per_question_results'][i]['retrieval_metrics'].get('recall_at_10', 'N/A')
        c0_mrr = results['C0']['per_question_results'][i]['retrieval_metrics'].get('mrr', 'N/A')
        
        for name in ['C0', 'W1', 'W2', 'W3']:
            q_result = results[name]['per_question_results'][i]
            recall5 = q_result['retrieval_metrics'].get('recall_at_5', 'N/A')
            recall10 = q_result['retrieval_metrics'].get('recall_at_10', 'N/A')
            mrr = q_result['retrieval_metrics'].get('mrr', 'N/A')
            pages = q_result.get('retrieved_pages', [])
            pages_str = str(pages)[:48]
            
            # Determine change
            if name == 'C0':
                change = '-'
            else:
                changes = []
                if recall5 != 'N/A' and c0_recall5 != 'N/A':
                    if recall5 > c0_recall5:
                        changes.append('R@5↑')
                    elif recall5 < c0_recall5:
                        changes.append('R@5↓')
                if recall10 != 'N/A' and c0_recall10 != 'N/A':
                    if recall10 > c0_recall10:
                        changes.append('R@10↑')
                    elif recall10 < c0_recall10:
                        changes.append('R@10↓')
                if mrr != 'N/A' and c0_mrr != 'N/A':
                    if mrr > c0_mrr:
                        changes.append('MRR↑')
                    elif mrr < c0_mrr:
                        changes.append('MRR↓')
                change = ', '.join(changes) if changes else 'No change'
            
            recall5_str = f"{recall5:.3f}" if recall5 != 'N/A' else 'N/A'
            recall10_str = f"{recall10:.3f}" if recall10 != 'N/A' else 'N/A'
            mrr_str = f"{mrr:.3f}" if mrr != 'N/A' else 'N/A'
            
            print(f"{name:<10} | {recall5_str:<10} | {recall10_str:<11} | {mrr_str:<10} | {pages_str:<50} | {change}")
    
    print("="*120)

def analyze_q3_q4_q7_q8():
    """Detailed analysis of q3, q4, q7, q8 with chunk ranking information."""
    configs = [
        ("C0", "evaluation/results/phase8_rrf_control_1_0.json"),
        ("W1", "evaluation/results/phase8_rrf_weighted_1_2_0_8.json"),
        ("W2", "evaluation/results/phase8_rrf_weighted_1_4_0_6.json"),
        ("W3", "evaluation/results/phase8_rrf_weighted_1_6_0_4.json"),
    ]
    
    results = {name: load_results(path) for name, path in configs}
    
    print("\n" + "="*100)
    print("DETAILED ANALYSIS: Q3, Q4, Q7, Q8")
    print("="*100)
    
    # Map question indices (0-indexed in array)
    questions_of_interest = {
        'q3': (2, "What workloads are used for evaluation?"),
        'q4': (3, "What are the reported evaluation results or metrics?"),
        'q7': (6, "Why does the evaluation intentionally restrict CPU cores?"),
        'q8': (7, "What container technology is used and what does it enable?"),
    }
    
    for q_id, (idx, q_text) in questions_of_interest.items():
        print(f"\n{q_id.upper()}: {q_text}")
        print("-"*100)
        
        # Get relevant pages from ground truth
        c0_result = results['C0']['per_question_results'][idx]
        relevant_pages = c0_result.get('relevant_pages', [])
        print(f"Relevant pages (ground truth): {relevant_pages}")
        
        # Per-config analysis
        print(f"\n{'Config':<10} | {'Recall@5':<10} | {'Recall@10':<11} | {'MRR':<10} | {'Top-5 Pages':<30} | Top-10 Pages")
        print("-"*100)
        
        for name in ['C0', 'W1', 'W2', 'W3']:
            q_result = results[name]['per_question_results'][idx]
            recall5 = q_result['retrieval_metrics'].get('recall_at_5', 'N/A')
            recall10 = q_result['retrieval_metrics'].get('recall_at_10', 'N/A')
            mrr = q_result['retrieval_metrics'].get('mrr', 'N/A')
            pages = q_result.get('retrieved_pages', [])
            
            top5_pages = str(pages[:5])
            top10_pages = str(pages)
            
            recall5_str = f"{recall5:.3f}" if recall5 != 'N/A' else 'N/A'
            recall10_str = f"{recall10:.3f}" if recall10 != 'N/A' else 'N/A'
            mrr_str = f"{mrr:.3f}" if mrr != 'N/A' else 'N/A'
            
            print(f"{name:<10} | {recall5_str:<10} | {recall10_str:<11} | {mrr_str:<10} | {top5_pages:<30} | {top10_pages}")
        
        print()
    
    print("="*100)
    print("\nNOTE: Detailed chunk-level ranking (dense rank, BM25 rank, RRF rank) requires")
    print("access to intermediate retrieval results, which are not stored in result files.")
    print("This information was available during Phase 8 audit diagnostic runs but is not")
    print("persisted in the final evaluation output.")
    print("="*100)

def main():
    """Run complete verification."""
    print("\n" + "="*100)
    print("PHASE 8 FINAL VERIFICATION")
    print("Extracting measured results from experimental output files")
    print("="*100)
    
    print_complete_metrics()
    analyze_per_question()
    analyze_q3_q4_q7_q8()
    
    print("\n" + "="*100)
    print("VERIFICATION COMPLETE")
    print("="*100)

if __name__ == '__main__':
    main()
