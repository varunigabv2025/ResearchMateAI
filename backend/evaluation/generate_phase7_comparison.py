"""
Phase 7 Comparison Report Generator

Compares HYBRID retrieval with default candidate pools (20+20) vs expanded pools (50+50)
to test the candidate-pool truncation hypothesis.
"""
import json
from pathlib import Path
from typing import Dict, List


def load_results(filepath: str) -> Dict:
    """Load evaluation results from JSON."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def compute_metric_comparison(control: float, treatment: float) -> Dict:
    """Compute absolute and relative changes."""
    absolute = treatment - control
    if control != 0:
        percent = (absolute / control) * 100
    else:
        percent = float('inf') if treatment > 0 else 0
    
    return {
        'control': control,
        'treatment': treatment,
        'absolute_change': absolute,
        'percent_change': percent
    }


def analyze_difficult_questions(control_results: Dict, treatment_results: Dict) -> Dict:
    """Analyze performance on q3, q4, q7, q8."""
    difficult_ids = ['q3', 'q4', 'q7', 'q8']
    analysis = {}
    
    for results, label in [(control_results, 'control'), (treatment_results, 'treatment')]:
        for q_result in results['per_question_results']:
            q_id = q_result['question_id']
            if q_id in difficult_ids:
                if q_id not in analysis:
                    analysis[q_id] = {
                        'question': q_result['question'][:80] + '...',
                        'relevant_pages': q_result.get('relevant_pages', [])
                    }
                
                analysis[q_id][label] = {
                    'recall_at_5': q_result['retrieval_metrics'].get('recall_at_5', 0),
                    'recall_at_10': q_result['retrieval_metrics'].get('recall_at_10', 0),
                    'mrr': q_result['retrieval_metrics'].get('mrr', 0),
                    'retrieved_pages': q_result.get('retrieved_pages', [])[:10]
                }
    
    return analysis


def generate_comparison_report(control_path: str, treatment_path: str, output_path: str):
    """
    Generate Phase 7 comparison report.
    
    Args:
        control_path: Path to control results (HYBRID 20+20)
        treatment_path: Path to treatment results (HYBRID 50+50)
        output_path: Path to output comparison JSON
    """
    control = load_results(control_path)
    treatment = load_results(treatment_path)
    
    # Extract configurations
    control_config = control['rag_config']['retrieval']
    treatment_config = treatment['rag_config']['retrieval']
    
    # Compute metric comparisons
    metrics_to_compare = [
        'hit_rate_at_1', 'hit_rate_at_3', 'hit_rate_at_5', 'hit_rate_at_10',
        'recall_at_1', 'recall_at_3', 'recall_at_5', 'recall_at_10',
        'precision_at_1', 'precision_at_3', 'precision_at_5', 'precision_at_10',
        'mrr'
    ]
    
    metric_comparisons = {}
    for metric in metrics_to_compare:
        control_val = control['retrieval_metrics'][metric]
        treatment_val = treatment['retrieval_metrics'][metric]
        metric_comparisons[metric] = compute_metric_comparison(control_val, treatment_val)
    
    # Latency comparison
    latency_comparison = {
        'control_mean_ms': control['latency_metrics']['retrieval']['mean'] * 1000,
        'treatment_mean_ms': treatment['latency_metrics']['retrieval']['mean'] * 1000,
        'control_std_ms': control['latency_metrics']['retrieval']['std_dev'] * 1000,
        'treatment_std_ms': treatment['latency_metrics']['retrieval']['std_dev'] * 1000,
        'overhead_ms': (treatment['latency_metrics']['retrieval']['mean'] - 
                       control['latency_metrics']['retrieval']['mean']) * 1000
    }
    
    # Difficult questions analysis
    difficult_analysis = analyze_difficult_questions(control, treatment)
    
    # Generate report
    report = {
        'phase': 'Phase 7: Candidate Pool Expansion Experiment',
        'timestamp': treatment['timestamp'],
        'hypothesis': 'Expanding dense and lexical candidate pools from 20 to 50 will improve Recall@10 by allowing relevant chunks that are currently eliminated before RRF fusion to enter the candidate set',
        'paper': treatment['paper'],
        'control': {
            'description': 'HYBRID retrieval with default candidate pools',
            'dense_pool': control_config.get('dense_candidate_pool', 'default(20)'),
            'lexical_pool': control_config.get('lexical_candidate_pool', 'default(20)'),
            'rrf_k': 60,
            'result_file': Path(control_path).name
        },
        'treatment': {
            'description': 'HYBRID retrieval with expanded candidate pools',
            'dense_pool': treatment_config.get('dense_candidate_pool', 50),
            'lexical_pool': treatment_config.get('lexical_candidate_pool', 50),
            'rrf_k': 60,
            'result_file': Path(treatment_path).name
        },
        'primary_metrics': {
            'recall_at_10': metric_comparisons['recall_at_10'],
            'recall_at_5': metric_comparisons['recall_at_5'],
            'mrr': metric_comparisons['mrr']
        },
        'all_metrics': metric_comparisons,
        'latency': latency_comparison,
        'difficult_questions': difficult_analysis,
        'evaluation_criteria': {
            'success': {
                'recall_at_10_improvement': '≥10% absolute (0.722 → 0.82+)',
                'q4_or_q7_recovery': 'At least one achieves Recall@10 > 0',
                'latency_overhead': '<200ms acceptable'
            },
            'failure': {
                'recall_at_10_improvement': '<5% absolute',
                'q4_and_q7_both_zero': 'Both remain at 0% recall',
                'latency_overhead': '>500ms unacceptable'
            }
        }
    }
    
    # Add conclusion based on evidence
    recall10_control = metric_comparisons['recall_at_10']['control']
    recall10_treatment = metric_comparisons['recall_at_10']['treatment']
    recall10_abs_change = metric_comparisons['recall_at_10']['absolute_change']
    
    q4_control_recall10 = difficult_analysis.get('q4', {}).get('control', {}).get('recall_at_10', 0)
    q4_treatment_recall10 = difficult_analysis.get('q4', {}).get('treatment', {}).get('recall_at_10', 0)
    q7_control_recall10 = difficult_analysis.get('q7', {}).get('control', {}).get('recall_at_10', 0)
    q7_treatment_recall10 = difficult_analysis.get('q7', {}).get('treatment', {}).get('recall_at_10', 0)
    
    latency_overhead = latency_comparison['overhead_ms']
    
    # Determine hypothesis outcome
    if recall10_abs_change >= 0.10 and (q4_treatment_recall10 > 0 or q7_treatment_recall10 > 0) and latency_overhead < 200:
        hypothesis_outcome = 'SUPPORTED'
        conclusion = f'Hypothesis SUPPORTED: Recall@10 improved by {recall10_abs_change:.3f} ({recall10_abs_change/recall10_control*100:.1f}%), at least one previously-failing question recovered, latency overhead acceptable ({latency_overhead:.1f}ms).'
    elif recall10_abs_change >= 0.05:
        hypothesis_outcome = 'PARTIALLY SUPPORTED'
        conclusion = f'Hypothesis PARTIALLY SUPPORTED: Recall@10 improved by {recall10_abs_change:.3f} ({recall10_abs_change/recall10_control*100:.1f}%), but some success criteria not fully met.'
    else:
        hypothesis_outcome = 'REJECTED'
        conclusion = f'Hypothesis REJECTED: Recall@10 improvement insufficient ({recall10_abs_change:.3f}, {recall10_abs_change/recall10_control*100:.1f}%). Candidate-pool size is NOT the primary bottleneck.'
    
    report['hypothesis_outcome'] = hypothesis_outcome
    report['scientific_conclusion'] = conclusion
    
    # Save report
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*80}")
    print("PHASE 7 COMPARISON REPORT")
    print('='*80)
    print(f"\nHypothesis: {report['hypothesis']}")
    print(f"\nControl: {report['control']['description']}")
    print(f"  Dense pool: {report['control']['dense_pool']}")
    print(f"  Lexical pool: {report['control']['lexical_pool']}")
    print(f"\nTreatment: {report['treatment']['description']}")
    print(f"  Dense pool: {report['treatment']['dense_pool']}")
    print(f"  Lexical pool: {report['treatment']['lexical_pool']}")
    print(f"\n{'='*80}")
    print("PRIMARY METRICS")
    print('='*80)
    
    for metric_name in ['recall_at_10', 'recall_at_5', 'mrr']:
        m = report['primary_metrics'][metric_name]
        print(f"\n{metric_name.upper()}:")
        print(f"  Control:   {m['control']:.4f}")
        print(f"  Treatment: {m['treatment']:.4f}")
        print(f"  Change:    {m['absolute_change']:+.4f} ({m['percent_change']:+.2f}%)")
    
    print(f"\n{'='*80}")
    print("LATENCY")
    print('='*80)
    print(f"Control:   {latency_comparison['control_mean_ms']:.1f}ms ± {latency_comparison['control_std_ms']:.1f}ms")
    print(f"Treatment: {latency_comparison['treatment_mean_ms']:.1f}ms ± {latency_comparison['treatment_std_ms']:.1f}ms")
    print(f"Overhead:  {latency_overhead:+.1f}ms")
    
    print(f"\n{'='*80}")
    print("DIFFICULT QUESTIONS (q3, q4, q7, q8)")
    print('='*80)
    
    for q_id in ['q3', 'q4', 'q7', 'q8']:
        if q_id in difficult_analysis:
            q = difficult_analysis[q_id]
            print(f"\n{q_id}: {q['question']}")
            print(f"  Relevant pages: {q['relevant_pages']}")
            print(f"  Control Recall@10:   {q['control']['recall_at_10']:.3f}")
            print(f"  Treatment Recall@10: {q['treatment']['recall_at_10']:.3f}")
            if q['control']['recall_at_10'] == 0 and q['treatment']['recall_at_10'] > 0:
                print(f"  *** RECOVERED from 0% ***")
    
    print(f"\n{'='*80}")
    print("HYPOTHESIS OUTCOME")
    print('='*80)
    print(f"\n{hypothesis_outcome}")
    print(f"\n{conclusion}")
    print(f"\n{'='*80}")
    print(f"\nReport saved to: {output_path}")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) != 4:
        print("Usage: python generate_phase7_comparison.py <control_results.json> <treatment_results.json> <output.json>")
        sys.exit(1)
    
    control_path = sys.argv[1]
    treatment_path = sys.argv[2]
    output_path = sys.argv[3]
    
    generate_comparison_report(control_path, treatment_path, output_path)
