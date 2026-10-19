"""
Phase 9A Experiment Runner
Runs all configurations on the expanded 25-question benchmark.
"""
import subprocess
import sys
from pathlib import Path
import time

# Paper ID (PA-EIS)
PAPER_ID = '075cdd7f-bff1-43fd-a52c-bba13a64acda'
DATASET = 'backend/evaluation/dataset_phase9a.json'

# Experimental configurations
CONFIGURATIONS = [
    {
        'name': 'Phase9A_Dense',
        'mode': 'dense',
        'output': 'backend/evaluation/results/phase9a_dense.json',
        'description': 'Dense-only baseline'
    },
    {
        'name': 'Phase9A_Hybrid',
        'mode': 'hybrid',
        'output': 'backend/evaluation/results/phase9a_hybrid.json',
        'description': 'Hybrid (Dense + BM25 + RRF, α=1.0, β=1.0)'
    },
    {
        'name': 'Phase9A_RRF_W1',
        'mode': 'hybrid',
        'rrf_alpha': 1.2,
        'rrf_beta': 0.8,
        'output': 'backend/evaluation/results/phase9a_rrf_weighted_1_2_0_8.json',
        'description': 'Weighted RRF W1 (α=1.2, β=0.8)'
    },
    {
        'name': 'Phase9A_RRF_W2',
        'mode': 'hybrid',
        'rrf_alpha': 1.4,
        'rrf_beta': 0.6,
        'output': 'backend/evaluation/results/phase9a_rrf_weighted_1_4_0_6.json',
        'description': 'Weighted RRF W2 (α=1.4, β=0.6)'
    },
    {
        'name': 'Phase9A_RRF_W3',
        'mode': 'hybrid',
        'rrf_alpha': 1.6,
        'rrf_beta': 0.4,
        'output': 'backend/evaluation/results/phase9a_rrf_weighted_1_6_0_4.json',
        'description': 'Weighted RRF W3 (α=1.6, β=0.4)'
    },
]

def run_experiment(config):
    """Run a single experiment configuration."""
    print(f"\n{'='*80}")
    print(f"Running: {config['name']}")
    print(f"Description: {config['description']}")
    print(f"{'='*80}\n")
    
    # Build command (run from backend directory to ensure correct database path)
    cmd = [
        sys.executable,
        'evaluation/run_evaluation.py',
        '--paper-id', PAPER_ID,
        '--dataset', '../' + DATASET,  # Adjust path since we're running from backend/
        '--mode', config['mode'],
        '--output', '../' + config['output'],  # Adjust path
        '--skip-llm'  # Retrieval-only evaluation
    ]
    
    # Add RRF weights if specified
    if 'rrf_alpha' in config:
        cmd.extend(['--rrf-alpha', str(config['rrf_alpha'])])
    if 'rrf_beta' in config:
        cmd.extend(['--rrf-beta', str(config['rrf_beta'])])
    
    print(f"Command: {' '.join(cmd)}\n")
    
    # Run experiment (from backend directory to ensure correct database path)
    start_time = time.time()
    try:
        result = subprocess.run(
            cmd, 
            cwd=str(Path(__file__).parent.parent),  # Run from backend/
            check=True, 
            capture_output=True, 
            text=True
        )
        elapsed = time.time() - start_time
        
        print(f"✓ {config['name']} completed in {elapsed:.1f}s")
        print(f"Output: {config['output']}\n")
        
        # Show last few lines of output
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 5:
                print("Last output lines:")
                for line in lines[-5:]:
                    print(f"  {line}")
        
        return True
    except subprocess.CalledProcessError as e:
        elapsed = time.time() - start_time
        print(f"✗ {config['name']} FAILED after {elapsed:.1f}s")
        print(f"Error: {e}")
        if e.stdout:
            print(f"Stdout: {e.stdout}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        return False

def main():
    """Run all Phase 9A experiments."""
    print("\n" + "="*80)
    print("PHASE 9A EXPERIMENT SUITE")
    print("="*80)
    print(f"\nDataset: {DATASET}")
    print(f"Paper ID: {PAPER_ID}")
    print(f"Configurations: {len(CONFIGURATIONS)}")
    print(f"Questions per config: 25")
    print("\nNOTE: Running retrieval-only evaluation (--skip-llm)")
    print("="*80)
    
    # Run each configuration
    results = {}
    for config in CONFIGURATIONS:
        success = run_experiment(config)
        results[config['name']] = success
    
    # Summary
    print("\n" + "="*80)
    print("PHASE 9A EXPERIMENT SUMMARY")
    print("="*80)
    
    successful = sum(1 for success in results.values() if success)
    failed = len(results) - successful
    
    print(f"\n[+] Successful: {successful}/{len(CONFIGURATIONS)}")
    print(f"[-] Failed: {failed}/{len(CONFIGURATIONS)}")
    
    if failed == 0:
        print("\n[SUCCESS] All experiments completed successfully")
        print("\nNext steps:")
        print("  1. Review results in backend/evaluation/results/")
        print("  2. Run analysis: python backend/evaluation/analyze_phase9a_results.py")
        print("  3. Generate report")
    else:
        print("\n⚠️  Some experiments failed. Review errors above.")
        for name, success in results.items():
            if not success:
                print(f"  [FAIL] {name}")
    
    return failed == 0

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
