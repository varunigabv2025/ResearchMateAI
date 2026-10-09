"""
Phase 9A Final Review Script
Independent verification of Phase 9A implementation.
"""
import json
from pathlib import Path
import sys

def review_dataset_integrity():
    """Review 1: Dataset Integrity."""
    print("\n" + "="*80)
    print("1. DATASET INTEGRITY CHECK")
    print("="*80)
    
    # Load datasets
    orig = json.load(open('backend/evaluation/dataset.json'))
    phase9a = json.load(open('backend/evaluation/dataset_phase9a.json'))
    
    print(f"\nOriginal dataset questions: {len(orig['questions'])}")
    print(f"Phase 9A dataset questions: {len(phase9a['questions'])}")
    
    # Count by phase
    orig_count = sum(1 for q in phase9a['questions'] if q.get('phase') == 'original')
    new_count = sum(1 for q in phase9a['questions'] if q.get('phase') == 'phase9a')
    print(f"Phase 9A original questions: {orig_count}")
    print(f"Phase 9A new questions: {new_count}")
    
    issues = []
    
    # Check counts
    if len(phase9a['questions']) != 25:
        issues.append(f"CRITICAL: Expected 25 questions, got {len(phase9a['questions'])}")
    if orig_count != 10:
        issues.append(f"CRITICAL: Expected 10 original questions, got {orig_count}")
    if new_count != 15:
        issues.append(f"CRITICAL: Expected 15 new questions, got {new_count}")
    
    # Check for duplicates
    ids = [q['id'] for q in phase9a['questions']]
    if len(ids) != len(set(ids)):
        issues.append(f"CRITICAL: Duplicate question IDs found")
    
    # Verify original questions unchanged
    print("\nVerifying original questions unchanged:")
    orig_q_map = {q['id']: q for q in orig['questions']}
    phase9a_orig = {q['id']: q for q in phase9a['questions'] if q.get('phase') == 'original'}
    
    for qid in ['q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8', 'q9', 'q10']:
        if qid not in phase9a_orig:
            issues.append(f"CRITICAL: {qid} missing from Phase 9A")
            continue
        
        o = orig_q_map[qid]
        p = phase9a_orig[qid]
        
        if o['question'] != p['question']:
            issues.append(f"CRITICAL: {qid} question text changed")
            print(f"  {qid}: QUESTION TEXT CHANGED")
        elif o['relevant_pages'] != p['relevant_pages']:
            issues.append(f"MAJOR: {qid} relevant_pages changed")
            print(f"  {qid}: relevant_pages changed")
        elif o['answerable'] != p['answerable']:
            issues.append(f"CRITICAL: {qid} answerable changed")
            print(f"  {qid}: answerable changed")
        else:
            print(f"  {qid}: OK")
    
    if not issues:
        print("\n✓ Dataset integrity: PASSED")
    else:
        print(f"\n✗ Dataset integrity: {len(issues)} issues found")
        for issue in issues:
            print(f"  - {issue}")
    
    return issues

def review_results():
    """Review 6: Result Verification."""
    print("\n" + "="*80)
    print("6. RESULT VERIFICATION")
    print("="*80)
    
    configs = [
        ('Dense', 'backend/evaluation/results/phase9a_dense.json', 0.590, 0.530),
        ('Hybrid', 'backend/evaluation/results/phase9a_hybrid.json', 0.854, 0.599),
        ('W1', 'backend/evaluation/results/phase9a_rrf_weighted_1_2_0_8.json', 0.750, 0.545),
        ('W2', 'backend/evaluation/results/phase9a_rrf_weighted_1_4_0_6.json', 0.750, 0.545),
        ('W3', 'backend/evaluation/results/phase9a_rrf_weighted_1_6_0_4.json', 0.750, 0.545),
    ]
    
    issues = []
    
    print(f"\n{'Config':<10} | {'R@10 (Actual)':<15} | {'R@10 (Claimed)':<16} | {'MRR (Actual)':<15} | {'MRR (Claimed)':<15} | Match")
    print("-" * 100)
    
    for name, path, claimed_r10, claimed_mrr in configs:
        try:
            with open(path) as f:
                data = json.load(f)
            
            actual_r10 = data['retrieval_metrics']['recall_at_10']
            actual_mrr = data['retrieval_metrics']['mrr']
            
            r10_match = abs(actual_r10 - claimed_r10) < 0.001
            mrr_match = abs(actual_mrr - claimed_mrr) < 0.001
            
            match_str = "✓" if (r10_match and mrr_match) else "✗"
            
            print(f"{name:<10} | {actual_r10:<15.3f} | {claimed_r10:<16.3f} | {actual_mrr:<15.3f} | {claimed_mrr:<15.3f} | {match_str}")
            
            if not r10_match:
                issues.append(f"MAJOR: {name} R@10 mismatch: actual={actual_r10:.3f}, claimed={claimed_r10:.3f}")
            if not mrr_match:
                issues.append(f"MAJOR: {name} MRR mismatch: actual={actual_mrr:.3f}, claimed={claimed_mrr:.3f}")
                
        except FileNotFoundError:
            issues.append(f"CRITICAL: Result file missing: {path}")
            print(f"{name:<10} | FILE NOT FOUND")
        except Exception as e:
            issues.append(f"CRITICAL: Error reading {name}: {e}")
            print(f"{name:<10} | ERROR: {e}")
    
    if not issues:
        print("\n✓ Result verification: PASSED")
    else:
        print(f"\n✗ Result verification: {len(issues)} issues found")
    
    return issues

def review_production_config():
    """Review 11: Production Configuration."""
    print("\n" + "="*80)
    print("11. PRODUCTION CONFIGURATION VERIFICATION")
    print("="*80)
    
    sys.path.insert(0, 'backend')
    from app.services.retrieval_service import RetrievalService
    
    s = RetrievalService()
    
    expected = {
        'DEFAULT_RRF_ALPHA': 1.0,
        'DEFAULT_RRF_BETA': 1.0,
        'DEFAULT_DENSE_K': 20,
        'DEFAULT_LEXICAL_K': 20,
        'DEFAULT_RRF_K': 60,
    }
    
    issues = []
    
    print("\nProduction defaults:")
    for key, expected_val in expected.items():
        actual_val = getattr(s, key)
        match = actual_val == expected_val
        status = "✓" if match else "✗"
        print(f"  {status} {key}: {actual_val} (expected: {expected_val})")
        
        if not match:
            issues.append(f"CRITICAL: {key} changed to {actual_val}, expected {expected_val}")
    
    if not issues:
        print("\n✓ Production configuration: UNCHANGED")
    else:
        print(f"\n✗ Production configuration: {len(issues)} issues found")
    
    return issues

def main():
    """Run all reviews."""
    print("\n" + "="*80)
    print("PHASE 9A FINAL REVIEW")
    print("="*80)
    
    all_issues = []
    
    all_issues.extend(review_dataset_integrity())
    all_issues.extend(review_results())
    all_issues.extend(review_production_config())
    
    # Summary
    print("\n" + "="*80)
    print("REVIEW SUMMARY")
    print("="*80)
    
    critical = [i for i in all_issues if i.startswith('CRITICAL')]
    major = [i for i in all_issues if i.startswith('MAJOR')]
    minor = [i for i in all_issues if i.startswith('MINOR')]
    
    print(f"\nTotal issues: {len(all_issues)}")
    print(f"  CRITICAL: {len(critical)}")
    print(f"  MAJOR: {len(major)}")
    print(f"  MINOR: {len(minor)}")
    
    if all_issues:
        print("\nIssues found:")
        for issue in all_issues:
            print(f"  - {issue}")
    
    # Verdict
    if critical:
        print("\n✗ VERDICT: NOT READY TO COMMIT (critical issues)")
    elif major:
        print("\n⚠ VERDICT: READY WITH MINOR FIXES (major issues)")
    else:
        print("\n✓ VERDICT: READY TO COMMIT")

if __name__ == '__main__':
    main()
