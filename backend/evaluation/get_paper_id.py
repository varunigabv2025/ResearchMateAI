"""
Helper script to find the paper ID for PA-EIS paper.
"""
import sys
sys.path.insert(0, '.')

from app.core.database import SessionLocal
from app.models import Paper

def get_paper_id():
    """Find PA-EIS paper ID."""
    db = SessionLocal()
    try:
        papers = db.query(Paper).all()
        
        print(f"Found {len(papers)} paper(s) in database:\n")
        
        for paper in papers:
            print(f"ID: {paper.id}")
            print(f"Filename: {paper.filename}")
            print(f"Original: {paper.original_filename}")
            print(f"Processed: {paper.processed}")
            print(f"Pages: {paper.page_count}")
            print("-" * 60)
        
        # Find PA-EIS paper
        pa_eis = db.query(Paper).filter(
            Paper.original_filename.like('%PA-EIS%') | Paper.original_filename.like('%PA_EIS%')
        ).first()
        
        if pa_eis:
            print(f"\n✓ Found PA-EIS paper:")
            print(f"  ID: {pa_eis.id}")
            print(f"  Filename: {pa_eis.filename}")
            print(f"  Original: {pa_eis.original_filename}")
            print(f"  Processed: {pa_eis.processed}")
            return str(pa_eis.id)
        else:
            print("\n✗ PA-EIS paper not found in database")
            print("Available papers:")
            for p in papers:
                print(f"  - {p.original_filename}")
            return None
            
    finally:
        db.close()

if __name__ == '__main__':
    paper_id = get_paper_id()
    if paper_id:
        print(f"\nTo run evaluation:")
        print(f"python evaluation/run_evaluation.py --paper-id {paper_id}")
