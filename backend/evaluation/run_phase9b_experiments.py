"""
Phase 9B Experiment Runner
Runs all configurations on the 50-question multi-paper benchmark.

Key differences from Phase 9A:
- Handles multiple paper_ids per question (cross-paper questions)
- Maps chunk_ids to page numbers for ground truth
- Aggregates retrieval results across papers
- 50 questions across 6 papers (vs. 25 questions on 1 paper)
"""
import subprocess
import sys
import json
import hashlib
from pathlib import Path
import time
from typing import Dict, List, Set
from datetime import datetime

# Dataset configuration
DATASET = 'backend/evaluation/dataset_phase9b.json'

# Paper IDs (Phase 9B corpus)
PAPER_IDS = {
    'resnet': '6c17e19e778c49feb63a78f385975434',
    'bert': '034186580f8045b9b20c84db274c63ae',
    'transformer': '82a45c626e6c4678b4dc60bc7e9167a2',
    'yolo': '3d33044cda464ede9ce821914baebfff',
    'mobilenets': 'aa0cbf1ec4f54ec5a37bcb16a1a562ba',
    'pruning_survey': 'b1b37ef43b7e47f9bdb1b400d62ab40d'
}

# Experimental configurations
CONFIGURATIONS = [
    {
        'name': 'Phase9B_Dense',
        'mode': 'dense',
        'output': 'backend/evaluation/results/phase9b_dense.json',
        'description': 'Dense-only baseline (vector similarity)'
    },
    {
        'name': 'Phase9B_Hybrid',
        'mode': 'hybrid',
        'output': 'backend/evaluation/results/phase9b_hybrid.json',
        'description': 'Hybrid (Dense + BM25 + RRF, α=1.0, β=1.0)'
    },
    {
        'name': 'Phase9B_RRF_W1',
        'mode': 'hybrid',
        'rrf_alpha': 1.2,
        'rrf_beta': 0.8,
        'output': 'backend/evaluation/results/phase9b_rrf_w1.json',
        'description': 'Weighted RRF W1 (α=1.2, β=0.8) - moderate dense preference'
    },
    {
        'name': 'Phase9B_RRF_W2',
        'mode': 'hybrid',
        'rrf_alpha': 1.4,
        'rrf_beta': 0.6,
        'output': 'backend/evaluation/results/phase9b_rrf_w2.json',
        'description': 'Weighted RRF W2 (α=1.4, β=0.6) - strong dense preference'
    },
    {
        'name': 'Phase9B_RRF_W3',
        'mode': 'hybrid',
        'rrf_alpha': 1.6,
        'rrf_beta': 0.4,
        'output': 'backend/evaluation/results/phase9b_rrf_w3.json',
        'description': 'Weighted RRF W3 (α=1.6, β=0.4) - very strong dense preference'
    },
]


def compute_dataset_hash(dataset_path: str) -> str:
    """Compute SHA256 hash of dataset file for reproducibility."""
    with open(dataset_path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def load_dataset(dataset_path: str) -> Dict:
    """Load evaluation dataset."""
    with open(dataset_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_chunk_to_page_mapping(dataset: Dict) -> Dict[str, int]:
    """
    Build mapping from chunk_id to page_number using dataset evidence.
    
    The Phase 9B dataset includes chunk_ids with page context in evidence_rationale.
    We extract this to create ground truth for retrieval evaluation.
    
    Returns:
        Dictionary mapping chunk_id (str) → page_number (int)
    """
    chunk_to_page = {}
    
    for question in dataset['questions']:
        chunk_ids = question.get('chunk_ids', [])
        
        # For Phase 9B, we'll need to query the database directly
        # since the dataset doesn't explicitly store page numbers per chunk
        # We'll rely on the existing evaluation framework's database queries
        
    return chunk_to_page


def get_paper_ids_for_question(question: Dict) -> List[str]:
    """
    Extract paper IDs for a question.
    
    Phase 9B dataset uses 'paper_ids' field (array).
    Phase 9A used 'paper_id' (single value).
    
    Returns:
        List of paper ID strings
    """
    # Try Phase 9B format first (array)
    if 'paper_ids' in question:
        paper_ids = question['paper_ids']
        if isinstance(paper_ids, list):
            return paper_ids
        else:
            return [paper_ids]
    
    # Fallback to Phase 9A format (single value)
    if 'paper_id' in question:
        return [question['paper_id']]
    
    return []


def run_evaluation_for_paper(
    paper_id: str,
    dataset_path: str,
    temp_output: str,
    mode: str,
    rrf_alpha: float = None,
    rrf_beta: float = None
) -> bool:
    """
    Run evaluation for a single paper.
    
    This is a helper for the multi-paper aggregation strategy.
    For cross-paper questions, we run retrieval on each cited paper independently.
    
    Args:
        paper_id: UUID of the paper
        dataset_path: Path to dataset
        temp_output: Temporary output file
        mode: Retrieval mode
        rrf_alpha: RRF alpha weight (optional)
        rrf_beta: RRF beta weight (optional)
        
    Returns:
        True if successful, False otherwise
    """
    cmd = [
        sys.executable,
        'evaluation/run_evaluation.py',
        '--paper-id', paper_id,
        '--dataset', '../' + dataset_path,
        '--mode', mode,
        '--output', '../' + temp_output,
        '--skip-llm'  # Retrieval-only evaluation
    ]
    
    # Add RRF weights if specified
    if rrf_alpha is not None:
        cmd.extend(['--rrf-alpha', str(rrf_alpha)])
    if rrf_beta is not None:
        cmd.extend(['--rrf-beta', str(rrf_beta)])
    
    try:
        result = subprocess.run(
            cmd,
            cwd=str(Path(__file__).parent.parent),  # Run from backend/
            check=True,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout for 50 questions
        )
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print(f"  [ERROR] Evaluation failed for paper {paper_id[:8]}...")
        if hasattr(e, 'stderr') and e.stderr:
            print(f"  Error: {e.stderr[:200]}")
        return False


def aggregate_multi_paper_results(
    question: Dict,
    paper_results: Dict[str, Dict]
) -> Dict:
    """
    Aggregate retrieval results across multiple papers for cross-paper questions.
    
    Strategy:
    - Combine retrieved_pages from all papers
    - Take union of retrieved chunks
    - Preserve per-paper retrieval metadata
    - Compute metrics against union of relevant_pages
    
    Args:
        question: Question data from dataset
        paper_results: Dictionary mapping paper_id → evaluation result
        
    Returns:
        Aggregated result for the question
    """
    question_id = question['id']
    
    # Collect all retrieved pages across papers
    all_retrieved_pages = []
    all_retrieved_chunks = []
    total_chunks = 0
    
    for paper_id, result in paper_results.items():
        # Find the question result in this paper's evaluation
        for q_result in result.get('per_question_results', []):
            if q_result['question_id'] == question_id:
                retrieved_pages = q_result.get('retrieved_pages', [])
                all_retrieved_pages.extend(retrieved_pages)
                total_chunks += q_result.get('retrieved_chunk_count', 0)
                break
    
    # Remove duplicate pages (keep order of first occurrence)
    seen = set()
    unique_retrieved_pages = []
    for page in all_retrieved_pages:
        if page not in seen:
            seen.add(page)
            unique_retrieved_pages.append(page)
    
    # Build aggregated result
    aggregated = {
        'question_id': question_id,
        'paper_count': len(paper_results),
        'retrieved_pages': unique_retrieved_pages,
        'retrieved_chunk_count': total_chunks,
        'unique_page_count': len(unique_retrieved_pages),
        'per_paper_results': {}
    }
    
    # Store per-paper results for analysis
    for paper_id, result in paper_results.items():
        for q_result in result.get('per_question_results', []):
            if q_result['question_id'] == question_id:
                aggregated['per_paper_results'][paper_id] = {
                    'retrieved_pages': q_result.get('retrieved_pages', []),
                    'retrieved_chunk_count': q_result.get('retrieved_chunk_count', 0),
                    'retrieval_latency_ms': q_result.get('retrieval_latency_ms', 0)
                }
                break
    
    return aggregated


def run_experiment(config: Dict) -> bool:
    """
    Run a single experiment configuration across all 50 questions.
    
    Phase 9B Approach:
    1. For single-paper questions: Run evaluation on that paper
    2. For multi-paper questions: Run evaluation on each paper, aggregate results
    3. Compute metrics using aggregated retrieved_pages
    
    Args:
        config: Configuration dictionary
        
    Returns:
        True if successful, False otherwise
    """
    print(f"\n{'='*80}")
    print(f"Running: {config['name']}")
    print(f"Description: {config['description']}")
    print(f"{'='*80}\n")
    
    start_time = time.time()
    
    # Load dataset
    dataset = load_dataset(DATASET)
    questions = dataset['questions']
    
    print(f"Dataset: {len(questions)} questions across {len(PAPER_IDS)} papers")
    print(f"Mode: {config['mode']}")
    if 'rrf_alpha' in config:
        print(f"RRF weights: α={config['rrf_alpha']}, β={config['rrf_beta']}")
    print()
    
    # Strategy: Run evaluation per-paper, then aggregate for cross-paper questions
    # This is more efficient than running 50 separate evaluations
    
    # Group questions by papers they reference
    paper_to_questions = {pid: [] for pid in PAPER_IDS.values()}
    
    for question in questions:
        paper_ids = get_paper_ids_for_question(question)
        for pid in paper_ids:
            if pid in paper_to_questions:
                paper_to_questions[pid].append(question['id'])
    
    print("Questions per paper:")
    for name, pid in PAPER_IDS.items():
        count = len(paper_to_questions[pid])
        print(f"  {name:20s}: {count:2d} questions")
    print()
    
    # For Phase 9B, we'll use a simpler approach:
    # Run evaluation on a "primary paper" and use the existing framework
    # For multi-paper questions, we'll run separate evaluations and aggregate
    
    # However, the existing run_evaluation.py is designed for single-paper
    # We need a different approach: custom evaluation loop
    
    print("NOTE: Multi-paper evaluation requires custom aggregation.")
    print("For Phase 9B-4, we'll run evaluations per-paper then aggregate.")
    print()
    
    # Create temporary output directory
    temp_dir = Path('backend/evaluation/results/temp')
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Run evaluation for each paper
    paper_results = {}
    
    for paper_name, paper_id in PAPER_IDS.items():
        print(f"[{paper_name}] Running evaluation...")
        
        temp_output = f"backend/evaluation/results/temp/{config['name']}_{paper_name}.json"
        
        success = run_evaluation_for_paper(
            paper_id=paper_id,
            dataset_path=DATASET,
            temp_output=temp_output,
            mode=config['mode'],
            rrf_alpha=config.get('rrf_alpha'),
            rrf_beta=config.get('rrf_beta')
        )
        
        if success:
            # Load results
            with open(temp_output, 'r', encoding='utf-8') as f:
                paper_results[paper_id] = json.load(f)
            print(f"  [OK] {paper_name} completed")
        else:
            print(f"  [FAIL] {paper_name} FAILED")
            return False
    
    # Aggregate results across papers
    print("\nAggregating multi-paper results...")
    
    aggregated_results = []
    
    for question in questions:
        question_id = question['id']
        paper_ids = get_paper_ids_for_question(question)
        
        # Collect relevant paper results
        question_paper_results = {
            pid: paper_results[pid]
            for pid in paper_ids
            if pid in paper_results
        }
        
        if len(paper_ids) == 1:
            # Single-paper question: use result directly
            paper_id = paper_ids[0]
            if paper_id in paper_results:
                for q_result in paper_results[paper_id]['per_question_results']:
                    if q_result['question_id'] == question_id:
                        aggregated_results.append(q_result)
                        break
        else:
            # Multi-paper question: aggregate
            aggregated = aggregate_multi_paper_results(question, question_paper_results)
            aggregated_results.append(aggregated)
    
    elapsed = time.time() - start_time
    
    print(f"\n[OK] {config['name']} completed in {elapsed:.1f}s")
    print(f"Output: {config['output']}\n")
    
    # Save aggregated results
    # Note: For Phase 9B, we need to restructure the output format
    # to match the existing evaluation schema while supporting multi-paper
    
    output_path = Path(config['output'])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Build final result structure
    final_result = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'evaluation_duration_seconds': elapsed,
        'configuration': {
            'name': config['name'],
            'description': config['description'],
            'mode': config['mode'],
            'rrf_alpha': config.get('rrf_alpha', 'default(1.0)'),
            'rrf_beta': config.get('rrf_beta', 'default(1.0)')
        },
        'dataset': {
            'name': dataset.get('dataset_name'),
            'description': dataset.get('description'),
            'question_count': len(questions),
            'paper_count': len(PAPER_IDS),
            'dataset_hash': compute_dataset_hash(DATASET)
        },
        'papers': {name: pid for name, pid in PAPER_IDS.items()},
        'per_question_results': aggregated_results,
        'notes': [
            'Phase 9B multi-paper evaluation',
            f'Retrieval mode: {config["mode"]}',
            'Multi-paper questions aggregated across papers',
            'Retrieval-only evaluation (--skip-llm)',
            'Ground truth based on chunk_ids from dataset'
        ]
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_result, f, indent=2, ensure_ascii=False)
    
    print(f"Results saved to: {output_path}")
    
    return True


def main():
    """Run all Phase 9B experiments."""
    print("\n" + "="*80)
    print("PHASE 9B EXPERIMENT SUITE")
    print("="*80)
    print(f"\nDataset: {DATASET}")
    print(f"Papers: {len(PAPER_IDS)}")
    print(f"Configurations: {len(CONFIGURATIONS)}")
    print(f"Questions per config: 50")
    print(f"\nNOTE: Running retrieval-only evaluation (--skip-llm)")
    print(f"NOTE: Multi-paper questions will be aggregated across papers")
    print("="*80)
    
    # Verify dataset exists
    if not Path(DATASET).exists():
        print(f"\n[ERROR] Dataset not found: {DATASET}")
        return False
    
    # Compute dataset hash for reproducibility
    dataset_hash = compute_dataset_hash(DATASET)
    print(f"\nDataset SHA256: {dataset_hash[:16]}...")
    
    # Run each configuration
    results = {}
    for config in CONFIGURATIONS:
        success = run_experiment(config)
        results[config['name']] = success
        
        if not success:
            print(f"\n[WARNING] {config['name']} failed. Continuing with remaining configs...")
    
    # Summary
    print("\n" + "="*80)
    print("PHASE 9B EXPERIMENT SUMMARY")
    print("="*80)
    
    successful = sum(1 for success in results.values() if success)
    failed = len(results) - successful
    
    print(f"\n[+] Successful: {successful}/{len(CONFIGURATIONS)}")
    print(f"[-] Failed: {failed}/{len(CONFIGURATIONS)}")
    
    if successful > 0:
        print("\n[SUCCESS] Evaluation completed for:")
        for name, success in results.items():
            if success:
                print(f"  [OK] {name}")
        
        print("\nNext steps:")
        print("  1. Review results in backend/evaluation/results/")
        print("  2. Run analysis: python backend/evaluation/analyze_phase9b_results.py")
        print("  3. Generate PHASE9B_4_EVALUATION_RESULTS.md")
    
    if failed > 0:
        print("\n[WARNING] Some experiments failed:")
        for name, success in results.items():
            if not success:
                print(f"  [FAIL] {name}")
    
    return successful > 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
