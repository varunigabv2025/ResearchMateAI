"""
Phase 8 Weighted RRF Experiment Runner

Runs the predefined experimental configurations:
- C0: alpha=1.0, beta=1.0 (control)
- W1: alpha=1.2, beta=0.8
- W2: alpha=1.4, beta=0.6
- W3: alpha=1.6, beta=0.4
"""
import asyncio
import subprocess
import sys
from pathlib import Path

# Paper ID (PA-EIS scheduling paper)
PAPER_ID = '075cdd7f-bff1-43fd-a52c-bba13a64acda'

# DATASET = 'backend/evaluation/dataset.json'

# Experimental configurations
CONFIGURATIONS = [
    {
        'name': 'C0_Control',
        'alpha': 1.0,
        'beta': 1.0,
        'output': 'evaluation/results/phase8_rrf_control_1_0.json',
        'description': 'Control: Equal weighting (standard RRF)'
    },
    {
        'name': 'W1',
        'alpha': 1.2,
        'beta': 0.8,
        'output': 'evaluation/results/phase8_rrf_weighted_1_2_0_8.json',
        'description': 'Treatment 1: Moderate dense boost (α=1.2, β=0.8)'
    },
    {
        'name': 'W2',
        'alpha': 1.4,
        'beta': 0.6,
        'output': 'evaluation/results/phase8_rrf_weighted_1_4_0_6.json',
        'description': 'Treatment 2: Strong dense boost (α=1.4, β=0.6)'
    },
    {
        'name': 'W3',
        'alpha': 1.6,
        'beta': 0.4,
        'output': 'evaluation/results/phase8_rrf_weighted_1_6_0_4.json',
        'description': 'Treatment 3: Very strong dense boost (α=1.6, β=0.4)'
    }
]


def run_evaluation(config):
    """
    Run a single evaluation configuration.
    
    Args:
        config: Configuration dictionary with alpha, beta, output
        
    Returns:
        True if successful, False otherwise
    """
    print(f"\n{'='*70}")
    print(f"Running: {config['name']}")
    print(f"Description: {config['description']}")
    print(f"Alpha: {config['alpha']}, Beta: {config['beta']}")
    print(f"Output: {config['output']}")
    print('='*70)
    
    cmd = [
        sys.executable,
        'evaluation/run_evaluation.py',
        '--paper-id', PAPER_ID,
        '--dataset', 'evaluation/dataset.json',
        '--output', config['output'],
        '--mode', 'hybrid',
        '--skip-llm',
        '--rrf-alpha', str(config['alpha']),
        '--rrf-beta', str(config['beta'])
    ]
    
    try:
        # Run from backend directory
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            cwd='backend'
        )
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        print(f"✓ {config['name']} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {config['name']} FAILED")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False


def main():
    """
    Run all Phase 8 experimental configurations sequentially.
    """
    print("\n" + "="*70)
    print("PHASE 8: WEIGHTED RRF EXPERIMENT")
    print("="*70)
    print(f"Paper ID: {PAPER_ID}")
    print(f"Dataset: evaluation/dataset.json")
    print(f"Mode: hybrid (RRF fusion)")
    print(f"Configurations: {len(CONFIGURATIONS)}")
    print("="*70)
    
    results = []
    for config in CONFIGURATIONS:
        success = run_evaluation(config)
        results.append((config['name'], success))
    
    # Summary
    print("\n" + "="*70)
    print("EXPERIMENT SUMMARY")
    print("="*70)
    for name, success in results:
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"{name}: {status}")
    
    total_success = sum(1 for _, success in results if success)
    print(f"\nCompleted: {total_success}/{len(CONFIGURATIONS)}")
    print("="*70)
    
    if total_success == len(CONFIGURATIONS):
        print("\nAll experiments completed successfully!")
        print("Next step: Generate comparison report with generate_phase8_comparison.py")
        return 0
    else:
        print("\nSome experiments failed. Please check the output above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
