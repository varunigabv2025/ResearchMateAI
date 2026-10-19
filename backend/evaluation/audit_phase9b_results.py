"""
Phase 9B-4.1 Final Results Audit
Independent verification of Phase 9B-4 experiment integrity and accuracy.
"""
import json
import statistics
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Tuple

# Result files to audit
RESULT_FILES = {
    'Dense': 'backend/evaluation/results/phase9b_dense.json',
    'Hybrid': 'backend/evaluation/results/phase9b_hybrid.json',
    'W1': 'backend/evaluation/results/phase9b_rrf_w1.json',
    'W2': 'backend/evaluation/results/phase9b_rrf_w2.json',
    'W3': 'backend/evaluation/results/phase9b_rrf_w3.json',
}

def load_result(file_path: str) -> Dict:
    """Load result file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def audit_file_structure(config_name: str, result: Dict) -> List[str]:
    """Audit basic file structure and completeness."""
    issues = []
    
    # Check required fields
    required_fields = ['timestamp', 'configuration', 'dataset', 'papers', 'per_question_results']
    for field in required_fields:
        if field not in result:
            issues.append(f"Missing required field: {field}")
    
    # Check question count
    per_q = result.get('per_question_results', [])
    if len(per_q) != 50:
        issues.append(f"Expected 50 questions, found {len(per_q)}")
    
    # Check for duplicate question IDs
    question_ids = [q['question_id'] for q in per_q]
    duplicates = [qid for qid, count in Counter(question_ids).items() if count > 1]
    if duplicates:
        issues.append(f"Duplicate question IDs: {duplicates}")
    
    # Check for missing question IDs (expected q9b_1 through q9b_50)
    expected_ids = {f"q9b_{i}" for i in range(1, 51)}
    actual_ids = set(question_ids)
    missing = expected_ids - actual_ids
    if missing:
        issues.append(f"Missing question IDs: {sorted(missing)}")
    
    # Check configuration metadata
    config = result.get('configuration', {})
    if config.get('name') != config_name:
        issues.append(f"Config name mismatch: expected {config_name}, got {config.get('name')}")
    
    return issues


def recalculate_metrics(result: Dict) -> Dict[str, float]:
    """Independently recalculate aggregate metrics from per-question results."""
    per_q = result['per_question_results']
    
    # Filter valid questions with retrieval metrics
    valid = [q for q in per_q if 'retrieval_metrics' in q and q['retrieval_metrics']]
    
    if not valid:
        return {}
    
    # Collect metric values
    metrics = defaultdict(list)
    for q in valid:
        rm = q['retrieval_metrics']
        for metric_name, value in rm.items():
            if isinstance(value, (int, float)):
                metrics[metric_name].append(value)
    
    # Compute means
    aggregated = {}
    for metric_name, values in metrics.items():
        if values:
            aggregated[metric_name] = statistics.mean(values)
    
    return aggregated


def compare_retrieved_pages(results: Dict[str, Dict]) -> Dict:
    """Compare retrieved pages across configurations to detect duplicates or anomalies."""
    comparisons = {}
    
    # Get first question from each config
    for config_name, result in results.items():
        per_q = result['per_question_results']
        if per_q:
            first_q = per_q[0]
            comparisons[config_name] = {
                'question_id': first_q['question_id'],
                'retrieved_pages': first_q.get('retrieved_pages', [])[:5],  # First 5 pages
                'chunk_count': first_q.get('retrieved_chunk_count', 0)
            }
    
    return comparisons


def check_weighted_rrf_differences(results: Dict[str, Dict]) -> Dict:
    """
    Check if W1, W2, W3 produce different per-question rankings from Dense.
    """
    findings = {}
    
    dense_result = results.get('Dense')
    if not dense_result:
        return {'error': 'Dense result not found'}
    
    dense_pages = {q['question_id']: q.get('retrieved_pages', []) 
                   for q in dense_result['per_question_results']}
    
    for config_name in ['W1', 'W2', 'W3']:
        if config_name not in results:
            continue
        
        config_result = results[config_name]
        config_pages = {q['question_id']: q.get('retrieved_pages', []) 
                       for q in config_result['per_question_results']}
        
        # Compare page rankings
        identical_count = 0
        different_count = 0
        different_questions = []
        
        for qid in dense_pages:
            if qid in config_pages:
                if dense_pages[qid] == config_pages[qid]:
                    identical_count += 1
                else:
                    different_count += 1
                    if len(different_questions) < 5:  # Sample first 5
                        different_questions.append({
                            'qid': qid,
                            'dense': dense_pages[qid][:3],
                            config_name: config_pages[qid][:3]
                        })
        
        findings[config_name] = {
            'identical_rankings': identical_count,
            'different_rankings': different_count,
            'sample_differences': different_questions
        }
    
    return findings


def check_hybrid_vs_dense(results: Dict[str, Dict]) -> Dict:
    """Verify Dense vs Hybrid metric differences."""
    dense = results.get('Dense')
    hybrid = results.get('Hybrid')
    
    if not dense or not hybrid:
        return {'error': 'Dense or Hybrid result not found'}
    
    dense_metrics = recalculate_metrics(dense)
    hybrid_metrics = recalculate_metrics(hybrid)
    
    comparison = {}
    for metric in ['hit_rate_at_5', 'recall_at_10', 'mrr']:
        comparison[metric] = {
            'dense': dense_metrics.get(metric, 0),
            'hybrid': hybrid_metrics.get(metric, 0),
            'difference': dense_metrics.get(metric, 0) - hybrid_metrics.get(metric, 0)
        }
    
    return comparison


def analyze_ground_truth(result: Dict) -> Dict:
    """Analyze ground truth coverage in dataset."""
    per_q = result['per_question_results']
    
    total_questions = len(per_q)
    questions_with_metrics = sum(1 for q in per_q if 'retrieval_metrics' in q and q['retrieval_metrics'])
    
    # Collect citation/relevance info
    total_relevant_pages = 0
    questions_by_relevant_count = defaultdict(int)
    
    for q in per_q:
        citation_metrics = q.get('citation_metrics', {})
        relevant_count = citation_metrics.get('relevant_count', 0)
        total_relevant_pages += relevant_count
        questions_by_relevant_count[relevant_count] += 1
    
    return {
        'total_questions': total_questions,
        'questions_with_metrics': questions_with_metrics,
        'avg_relevant_pages_per_question': total_relevant_pages / total_questions if total_questions > 0 else 0,
        'questions_by_relevant_count': dict(questions_by_relevant_count)
    }


def analyze_per_paper_performance(result: Dict) -> Dict:
    """Analyze performance per paper."""
    per_q = result['per_question_results']
    
    # Load dataset to get paper_ids per question
    try:
        with open('backend/evaluation/dataset_phase9b.json', 'r', encoding='utf-8') as f:
            dataset = json.load(f)
        
        qid_to_papers = {}
        for q in dataset['questions']:
            qid_to_papers[q['id']] = q.get('paper_ids', [])
    except Exception as e:
        return {'error': f'Could not load dataset: {e}'}
    
    # Group by paper
    paper_metrics = defaultdict(lambda: {'questions': [], 'hit_at_5': [], 'recall_at_5': [], 'mrr': []})
    
    for q in per_q:
        qid = q['question_id']
        papers = qid_to_papers.get(qid, [])
        rm = q.get('retrieval_metrics', {})
        
        if not rm:
            continue
        
        for paper_id in papers:
            paper_metrics[paper_id]['questions'].append(qid)
            paper_metrics[paper_id]['hit_at_5'].append(rm.get('hit_rate_at_5', 0))
            paper_metrics[paper_id]['recall_at_5'].append(rm.get('recall_at_5', 0))
            paper_metrics[paper_id]['mrr'].append(rm.get('mrr', 0))
    
    # Compute averages
    summary = {}
    paper_names = {
        '6c17e19e778c49feb63a78f385975434': 'ResNet',
        '034186580f8045b9b20c84db274c63ae': 'BERT',
        '82a45c626e6c4678b4dc60bc7e9167a2': 'Transformer',
        '3d33044cda464ede9ce821914baebfff': 'YOLO',
        'aa0cbf1ec4f54ec5a37bcb16a1a562ba': 'MobileNets',
        'b1b37ef43b7e47f9bdb1b400d62ab40d': 'Pruning Survey'
    }
    
    for paper_id, metrics in paper_metrics.items():
        paper_name = paper_names.get(paper_id, paper_id[:8])
        summary[paper_name] = {
            'question_count': len(metrics['questions']),
            'avg_hit_at_5': statistics.mean(metrics['hit_at_5']) if metrics['hit_at_5'] else 0,
            'avg_recall_at_5': statistics.mean(metrics['recall_at_5']) if metrics['recall_at_5'] else 0,
            'avg_mrr': statistics.mean(metrics['mrr']) if metrics['mrr'] else 0
        }
    
    return summary


def check_mislabeled_questions(result: Dict) -> Dict:
    """Check the two mislabeled questions (q9b_41, q9b_49)."""
    per_q = result['per_question_results']
    
    findings = {}
    for qid in ['q9b_41', 'q9b_49']:
        q = next((q for q in per_q if q['question_id'] == qid), None)
        if q:
            findings[qid] = {
                'question': q['question'],
                'category': q.get('category'),
                'retrieval_metrics': q.get('retrieval_metrics', {}),
                'paper_count': q.get('paper_count', 'N/A')
            }
    
    return findings


def main():
    """Run complete audit."""
    print("="*80)
    print("PHASE 9B-4.1 FINAL RESULTS AUDIT")
    print("="*80)
    print()
    
    # Load all results
    results = {}
    print("Loading result files...")
    for config_name, file_path in RESULT_FILES.items():
        if Path(file_path).exists():
            results[config_name] = load_result(file_path)
            print(f"  [OK] {config_name}: {file_path}")
        else:
            print(f"  [MISSING] {config_name}: {file_path}")
    print()
    
    if len(results) != 5:
        print(f"[ERROR] Expected 5 result files, found {len(results)}")
        return
    
    # 1. File structure audit
    print("="*80)
    print("1. FILE STRUCTURE AUDIT")
    print("="*80)
    print()
    
    all_structure_issues = {}
    for config_name, result in results.items():
        issues = audit_file_structure(config_name, result)
        all_structure_issues[config_name] = issues
        
        if issues:
            print(f"{config_name}:")
            for issue in issues:
                print(f"  [ISSUE] {issue}")
        else:
            print(f"{config_name}: OK (50 questions, no duplicates)")
    print()
    
    # 2. Independent metric recalculation
    print("="*80)
    print("2. INDEPENDENT METRIC RECALCULATION")
    print("="*80)
    print()
    
    recalculated = {}
    for config_name, result in results.items():
        metrics = recalculate_metrics(result)
        recalculated[config_name] = metrics
        
        print(f"{config_name}:")
        print(f"  Hit Rate@1:  {metrics.get('hit_rate_at_1', 0):.3f}")
        print(f"  Hit Rate@5:  {metrics.get('hit_rate_at_5', 0):.3f}")
        print(f"  Hit Rate@10: {metrics.get('hit_rate_at_10', 0):.3f}")
        print(f"  Recall@5:    {metrics.get('recall_at_5', 0):.3f}")
        print(f"  Recall@10:   {metrics.get('recall_at_10', 0):.3f}")
        print(f"  MRR:         {metrics.get('mrr', 0):.3f}")
        print()
    
    # 3. Weighted RRF investigation
    print("="*80)
    print("3. WEIGHTED RRF INVESTIGATION")
    print("="*80)
    print()
    
    rrf_diffs = check_weighted_rrf_differences(results)
    for config_name, finding in rrf_diffs.items():
        print(f"{config_name}:")
        print(f"  Identical rankings to Dense: {finding.get('identical_rankings', 0)}/50")
        print(f"  Different rankings from Dense: {finding.get('different_rankings', 0)}/50")
        
        if finding.get('sample_differences'):
            print(f"  Sample differences (first 3 pages):")
            for diff in finding['sample_differences'][:3]:
                print(f"    {diff['qid']}: Dense={diff['dense']}, {config_name}={diff[config_name]}")
        print()
    
    # 4. Dense vs Hybrid verification
    print("="*80)
    print("4. DENSE VS HYBRID VERIFICATION")
    print("="*80)
    print()
    
    dh_comparison = check_hybrid_vs_dense(results)
    if 'error' not in dh_comparison:
        for metric, values in dh_comparison.items():
            print(f"{metric}:")
            print(f"  Dense:  {values['dense']:.4f}")
            print(f"  Hybrid: {values['hybrid']:.4f}")
            print(f"  Diff:   {values['difference']:+.4f}")
            print()
    else:
        print(f"[ERROR] {dh_comparison['error']}")
    
    # 5. Ground truth analysis
    print("="*80)
    print("5. GROUND TRUTH ANALYSIS")
    print("="*80)
    print()
    
    gt_analysis = analyze_ground_truth(results['Dense'])
    print(f"Total questions: {gt_analysis['total_questions']}")
    print(f"Questions with metrics: {gt_analysis['questions_with_metrics']}")
    print(f"Avg relevant pages per question: {gt_analysis['avg_relevant_pages_per_question']:.2f}")
    print(f"\nQuestions by relevant page count:")
    for count, num_questions in sorted(gt_analysis['questions_by_relevant_count'].items()):
        print(f"  {count} relevant pages: {num_questions} questions")
    print()
    
    # 6. Per-paper analysis
    print("="*80)
    print("6. PER-PAPER PERFORMANCE (Dense)")
    print("="*80)
    print()
    
    per_paper = analyze_per_paper_performance(results['Dense'])
    if 'error' not in per_paper:
        print(f"{'Paper':<20} {'Questions':<12} {'Hit@5':<10} {'Recall@5':<12} {'MRR':<8}")
        print("-"*80)
        for paper_name, metrics in sorted(per_paper.items()):
            print(f"{paper_name:<20} {metrics['question_count']:<12} {metrics['avg_hit_at_5']:<10.3f} {metrics['avg_recall_at_5']:<12.3f} {metrics['avg_mrr']:<8.3f}")
    else:
        print(f"[ERROR] {per_paper['error']}")
    print()
    
    # 7. Mislabeled questions
    print("="*80)
    print("7. MISLABELED QUESTIONS (q9b_41, q9b_49)")
    print("="*80)
    print()
    
    mislabeled = check_mislabeled_questions(results['Dense'])
    for qid, info in mislabeled.items():
        print(f"{qid}:")
        print(f"  Question: {info['question'][:60]}...")
        print(f"  Category: {info['category']}")
        print(f"  Paper count: {info['paper_count']}")
        rm = info['retrieval_metrics']
        if rm:
            print(f"  Hit@5: {rm.get('hit_rate_at_5', 0):.3f}, Recall@5: {rm.get('recall_at_5', 0):.3f}")
        print()
    
    # 8. Configuration verification
    print("="*80)
    print("8. CONFIGURATION VERIFICATION")
    print("="*80)
    print()
    
    for config_name, result in results.items():
        config = result['configuration']
        print(f"{config_name}:")
        print(f"  Name: {config['name']}")
        print(f"  Mode: {config['mode']}")
        print(f"  RRF alpha: {config.get('rrf_alpha', 'N/A')}")
        print(f"  RRF beta: {config.get('rrf_beta', 'N/A')}")
        print()
    
    print("="*80)
    print("AUDIT COMPLETE")
    print("="*80)


if __name__ == '__main__':
    main()
