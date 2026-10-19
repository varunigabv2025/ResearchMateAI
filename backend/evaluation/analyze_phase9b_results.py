"""
Phase 9B Results Analysis
Analyzes retrieval performance across Dense, Hybrid, and weighted RRF configurations.
"""
import json
import statistics
from pathlib import Path
from typing import Dict, List
from collections import defaultdict

# Result files
RESULT_FILES = {
    'Dense': 'backend/evaluation/results/phase9b_dense.json',
    'Hybrid (a=1.0, b=1.0)': 'backend/evaluation/results/phase9b_hybrid.json',
    'W1 (a=1.2, b=0.8)': 'backend/evaluation/results/phase9b_rrf_w1.json',
    'W2 (a=1.4, b=0.6)': 'backend/evaluation/results/phase9b_rrf_w2.json',
    'W3 (a=1.6, b=0.4)': 'backend/evaluation/results/phase9b_rrf_w3.json',
}

def load_results(file_path: str) -> Dict:
    """Load results from JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def compute_aggregate_metrics(results: Dict) -> Dict:
    """
    Compute aggregate retrieval metrics across all questions.
    
    Returns metrics at k=1,3,5,10 for Hit Rate, Recall, Precision, and MRR.
    """
    per_question = results['per_question_results']
    
    # Skip questions without retrieval metrics (errors or multi-paper aggregated)
    valid_questions = [
        q for q in per_question
        if 'retrieval_metrics' in q and q['retrieval_metrics']
    ]
    
    if not valid_questions:
        return {}
    
    metrics = defaultdict(list)
    
    for q in valid_questions:
        rm = q['retrieval_metrics']
        for metric_name, value in rm.items():
            metrics[metric_name].append(value)
    
    # Compute means
    aggregated = {}
    for metric_name, values in metrics.items():
        aggregated[metric_name] = statistics.mean(values) if values else 0.0
    
    return aggregated


def categorize_questions(results: Dict) -> Dict[str, List]:
    """
    Categorize questions by type for breakout analysis.
    
    Categories:
    - single_paper: Questions citing only 1 paper
    - multi_paper: Questions citing 2+ papers
    - metadata: Questions in metadata categories
    """
    from backend.evaluation.validate_phase9b_dataset import load_dataset
    
    # Load dataset to get paper_ids per question
    dataset = load_dataset('backend/evaluation/dataset_phase9b.json')
    
    categorized = {
        'single_paper': [],
        'multi_paper': [],
        'metadata': []
    }
    
    for question in dataset['questions']:
        qid = question['id']
        paper_ids = question.get('paper_ids', [])
        category = question.get('category', '')
        
        # Find corresponding result
        result = None
        for q in results['per_question_results']:
            if q['question_id'] == qid:
                result = q
                break
        
        if not result:
            continue
        
        # Categorize
        if len(paper_ids) == 1:
            categorized['single_paper'].append(result)
        else:
            categorized['multi_paper'].append(result)
        
        if 'metadata' in category.lower():
            categorized['metadata'].append(result)
    
    return categorized


def compute_category_metrics(questions: List[Dict]) -> Dict:
    """Compute aggregate metrics for a category of questions."""
    valid_questions = [
        q for q in questions
        if 'retrieval_metrics' in q and q['retrieval_metrics']
    ]
    
    if not valid_questions:
        return {}
    
    metrics = defaultdict(list)
    
    for q in valid_questions:
        rm = q['retrieval_metrics']
        for metric_name, value in rm.items():
            metrics[metric_name].append(value)
    
    aggregated = {}
    for metric_name, values in metrics.items():
        aggregated[metric_name] = statistics.mean(values) if values else 0.0
    
    return aggregated


def analyze_all_configurations():
    """Analyze all available configurations."""
    print("="*80)
    print("PHASE 9B EVALUATION RESULTS ANALYSIS")
    print("="*80)
    print()
    
    # Load all available results
    loaded_results = {}
    for config_name, file_path in RESULT_FILES.items():
        if Path(file_path).exists():
            loaded_results[config_name] = load_results(file_path)
            print(f"[OK] Loaded: {config_name}")
        else:
            print(f"[SKIP] Not found: {config_name}")
    
    print()
    print(f"Loaded {len(loaded_results)}/{len(RESULT_FILES)} configurations")
    print()
    
    if not loaded_results:
        print("[ERROR] No result files found!")
        return
    
    # Aggregate metrics for each configuration
    print("="*80)
    print("AGGREGATE METRICS (All 50 Questions)")
    print("="*80)
    print()
    
    all_aggregates = {}
    for config_name, results in loaded_results.items():
        metrics = compute_aggregate_metrics(results)
        all_aggregates[config_name] = metrics
        
        print(f"{config_name}:")
        print(f"  Hit Rate@1:  {metrics.get('hit_rate_at_1', 0):.3f}")
        print(f"  Hit Rate@5:  {metrics.get('hit_rate_at_5', 0):.3f}")
        print(f"  Hit Rate@10: {metrics.get('hit_rate_at_10', 0):.3f}")
        print(f"  Recall@1:    {metrics.get('recall_at_1', 0):.3f}")
        print(f"  Recall@5:    {metrics.get('recall_at_5', 0):.3f}")
        print(f"  Recall@10:   {metrics.get('recall_at_10', 0):.3f}")
        print(f"  Precision@1: {metrics.get('precision_at_1', 0):.3f}")
        print(f"  Precision@5: {metrics.get('precision_at_5', 0):.3f}")
        print(f"  MRR:         {metrics.get('mrr', 0):.3f}")
        print()
    
    # Category breakout (using first available config as reference)
    first_config = list(loaded_results.values())[0]
    
    print("="*80)
    print("BREAKOUT BY QUESTION TYPE")
    print("="*80)
    print()
    
    try:
        categorized = categorize_questions(first_config)
        
        print(f"Single-Paper Questions: {len(categorized['single_paper'])}")
        print(f"Multi-Paper Questions:  {len(categorized['multi_paper'])}")
        print(f"Metadata Questions:     {len(categorized['metadata'])}")
        print()
        
        for config_name, results in loaded_results.items():
            categorized = categorize_questions(results)
            
            print(f"{config_name}:")
            
            # Single-paper
            sp_metrics = compute_category_metrics(categorized['single_paper'])
            print(f"  Single-Paper:")
            print(f"    Hit@5: {sp_metrics.get('hit_rate_at_5', 0):.3f}, Recall@5: {sp_metrics.get('recall_at_5', 0):.3f}, MRR: {sp_metrics.get('mrr', 0):.3f}")
            
            # Multi-paper
            mp_metrics = compute_category_metrics(categorized['multi_paper'])
            print(f"  Multi-Paper:")
            print(f"    Hit@5: {mp_metrics.get('hit_rate_at_5', 0):.3f}, Recall@5: {mp_metrics.get('recall_at_5', 0):.3f}, MRR: {mp_metrics.get('mrr', 0):.3f}")
            
            print()
    
    except Exception as e:
        print(f"[WARNING] Category breakout failed: {e}")
        print()
    
    # Comparison table
    print("="*80)
    print("CONFIGURATION COMPARISON")
    print("="*80)
    print()
    print(f"{'Configuration':<25} {'Hit@1':<8} {'Hit@5':<8} {'Recall@5':<10} {'MRR':<8}")
    print("-"*80)
    
    for config_name in ['Dense', 'Hybrid (a=1.0, b=1.0)', 'W1 (a=1.2, b=0.8)', 'W2 (a=1.4, b=0.6)', 'W3 (a=1.6, b=0.4)']:
        if config_name in all_aggregates:
            m = all_aggregates[config_name]
            print(f"{config_name:<25} {m.get('hit_rate_at_1', 0):>6.3f}  {m.get('hit_rate_at_5', 0):>6.3f}  {m.get('recall_at_5', 0):>8.3f}  {m.get('mrr', 0):>6.3f}")
    
    print()
    print("="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)


if __name__ == '__main__':
    analyze_all_configurations()
