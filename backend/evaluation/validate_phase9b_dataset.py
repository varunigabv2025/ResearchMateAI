"""
Phase 9B Dataset Validation Script
Validates the 50-question multi-paper benchmark dataset.
"""
import json
import sqlite3
from pathlib import Path
from collections import Counter
import re

def validate_dataset():
    """Validate Phase 9B dataset structure, content, and evidence."""
    
    dataset_path = Path(__file__).parent / "dataset_phase9b.json"
    db_path = Path(__file__).parent.parent / "test.db"
    
    print("="*80)
    print("PHASE 9B DATASET VALIDATION")
    print("="*80)
    
    # Load dataset
    with open(dataset_path) as f:
        phase9b = json.load(f)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get valid paper IDs and chunk IDs from database
    cursor.execute("SELECT id FROM papers")
    valid_paper_ids = set(row[0] for row in cursor.fetchall())
    
    cursor.execute("SELECT id, paper_id FROM paper_chunks")
    valid_chunk_ids = {}
    for chunk_id, paper_id in cursor.fetchall():
        valid_chunk_ids[chunk_id] = paper_id
    
    errors = []
    warnings = []
    
    # Test 1: Basic structure
    print("\n1. Dataset Structure")
    print("-"*80)
    
    if 'questions' not in phase9b:
        errors.append("Missing 'questions' field")
        print("   ❌ Missing questions field")
        return False
    
    questions = phase9b['questions']
    total_questions = len(questions)
    
    print(f"   Total questions: {total_questions}")
    
    if total_questions != 50:
        warnings.append(f"Expected 50 questions, got {total_questions}")
        print(f"   ⚠️  Expected 50 questions, got {total_questions}")
    else:
        print("   ✅ Target count achieved (50)")
    
    # Test 2: Question ID uniqueness
    print("\n2. Question ID Uniqueness")
    print("-"*80)
    
    question_ids = [q['id'] for q in questions]
    if len(question_ids) != len(set(question_ids)):
        errors.append("Duplicate question IDs found")
        duplicates = [qid for qid in question_ids if question_ids.count(qid) > 1]
        print(f"   ❌ Duplicates: {set(duplicates)}")
    else:
        print("   ✅ All question IDs unique")
    
    # Test 3: Required fields
    print("\n3. Required Fields")
    print("-"*80)
    
    required_fields = ['id', 'question', 'category', 'difficulty', 'paper_ids', 
                      'chunk_ids', 'expected_answer_contains', 'relevant_pages', 
                      'answerable', 'evidence_rationale', 'notes']
    
    missing_fields = []
    for q in questions:
        for field in required_fields:
            if field not in q:
                missing_fields.append(f"{q.get('id', 'UNKNOWN')}: missing '{field}'")
    
    if missing_fields:
        errors.extend(missing_fields[:10])  # Limit to first 10
        if len(missing_fields) > 10:
            errors.append(f"... and {len(missing_fields) - 10} more missing fields")
        print(f"   ❌ Missing fields in {len(set(m.split(':')[0] for m in missing_fields))} questions")
    else:
        print("   ✅ All required fields present")
    
    # Test 4: Valid paper IDs
    print("\n4. Paper ID Validation")
    print("-"*80)
    
    invalid_paper_ids = []
    for q in questions:
        for pid in q.get('paper_ids', []):
            if pid not in valid_paper_ids:
                invalid_paper_ids.append(f"{q['id']}: invalid paper_id {pid[:8]}...")
    
    if invalid_paper_ids:
        errors.extend(invalid_paper_ids[:5])
        print(f"   ❌ {len(invalid_paper_ids)} invalid paper ID references")
    else:
        print("   ✅ All paper IDs valid")
    
    # Test 5: Valid chunk IDs
    print("\n5. Chunk ID Validation")
    print("-"*80)
    
    invalid_chunk_ids = []
    chunk_paper_mismatches = []
    
    for q in questions:
        q_paper_ids = set(q.get('paper_ids', []))
        for cid in q.get('chunk_ids', []):
            if cid not in valid_chunk_ids:
                invalid_chunk_ids.append(f"{q['id']}: invalid chunk_id {cid[:8]}...")
            else:
                # Check if chunk belongs to cited paper
                chunk_paper = valid_chunk_ids[cid]
                if chunk_paper not in q_paper_ids:
                    chunk_paper_mismatches.append(
                        f"{q['id']}: chunk {cid[:8]}... belongs to paper {chunk_paper[:8]}... "
                        f"but question cites {[p[:8]+'...' for p in q_paper_ids]}"
                    )
    
    if invalid_chunk_ids:
        errors.extend(invalid_chunk_ids[:5])
        print(f"   ❌ {len(invalid_chunk_ids)} invalid chunk ID references")
    elif chunk_paper_mismatches:
        errors.extend(chunk_paper_mismatches[:5])
        print(f"   ❌ {len(chunk_paper_mismatches)} chunk/paper mismatches")
    else:
        print("   ✅ All chunk IDs valid and match cited papers")
    
    # Test 6: Page number validation
    print("\n6. Page Number Validation")
    print("-"*80)
    
    # Get page counts for each paper
    cursor.execute("""
        SELECT id, page_count
        FROM papers
        WHERE upload_timestamp >= '2026-10-18'
    """)
    paper_page_counts = dict(cursor.fetchall())
    
    invalid_pages = []
    for q in questions:
        for pid in q.get('paper_ids', []):
            if pid in paper_page_counts:
                max_pages = paper_page_counts[pid]
                for page in q.get('relevant_pages', []):
                    if page < 1 or page > max_pages:
                        invalid_pages.append(
                            f"{q['id']}: page {page} invalid for paper {pid[:8]}... "
                            f"(has {max_pages} pages)"
                        )
    
    if invalid_pages:
        errors.extend(invalid_pages[:5])
        print(f"   ❌ {len(invalid_pages)} invalid page numbers")
    else:
        print("   ✅ All page numbers within valid ranges")
    
    # Test 7: Question text uniqueness
    print("\n7. Question Text Uniqueness")
    print("-"*80)
    
    question_texts = [q['question'].lower().strip() for q in questions]
    duplicates = [qt for qt in question_texts if question_texts.count(qt) > 1]
    
    if duplicates:
        errors.append(f"Duplicate question text found: {len(set(duplicates))} questions")
        print(f"   ❌ {len(set(duplicates))} duplicate question texts")
    else:
        print("   ✅ All question texts unique")
    
    # Test 8: Near-duplicate detection (similarity)
    print("\n8. Near-Duplicate Detection")
    print("-"*80)
    
    def simple_similarity(s1, s2):
        """Simple word overlap similarity."""
        words1 = set(re.findall(r'\w+', s1.lower()))
        words2 = set(re.findall(r'\w+', s2.lower()))
        if not words1 or not words2:
            return 0
        return len(words1 & words2) / len(words1 | words2)
    
    near_duplicates = []
    for i, q1 in enumerate(questions):
        for j, q2 in enumerate(questions[i+1:], i+1):
            sim = simple_similarity(q1['question'], q2['question'])
            if sim > 0.7:  # High similarity threshold
                near_duplicates.append(
                    f"{q1['id']} and {q2['id']}: {sim:.2f} similarity"
                )
    
    if near_duplicates:
        warnings.extend(near_duplicates[:5])
        print(f"   ⚠️  {len(near_duplicates)} potential near-duplicates (>70% word overlap)")
    else:
        print("   ✅ No near-duplicates detected")
    
    # Test 9: Category distribution
    print("\n9. Category Distribution")
    print("-"*80)
    
    categories = [q['category'] for q in questions]
    category_counts = Counter(categories)
    
    print("   Categories:")
    for cat, count in sorted(category_counts.items()):
        print(f"     {cat}: {count}")
    
    print(f"   ✅ {len(category_counts)} unique categories")
    
    # Test 10: Difficulty distribution
    print("\n10. Difficulty Distribution")
    print("-"*80)
    
    difficulties = [q['difficulty'] for q in questions]
    valid_difficulties = ['easy', 'medium', 'hard']
    
    invalid_diff = [d for d in difficulties if d not in valid_difficulties]
    if invalid_diff:
        errors.append(f"Invalid difficulty levels: {set(invalid_diff)}")
        print(f"   ❌ Invalid difficulty levels: {set(invalid_diff)}")
    
    diff_counts = Counter(difficulties)
    print("   Difficulty levels:")
    for diff in valid_difficulties:
        count = diff_counts.get(diff, 0)
        print(f"     {diff}: {count}")
    
    if not invalid_diff:
        print("   ✅ All difficulty levels valid")
    
    # Test 11: Cross-paper questions
    print("\n11. Cross-Paper Questions")
    print("-"*80)
    
    multi_paper = [q for q in questions if len(q.get('paper_ids', [])) > 1]
    print(f"   Multi-paper questions: {len(multi_paper)}")
    
    for q in multi_paper:
        if len(q.get('paper_ids', [])) < 2:
            warnings.append(f"{q['id']}: marked cross-paper but <2 paper_ids")
    
    if len(multi_paper) >= 10:
        print(f"   ✅ Target achieved ({len(multi_paper)} cross-paper questions)")
    else:
        warnings.append(f"Only {len(multi_paper)} cross-paper questions (target: 10)")
        print(f"   ⚠️  Below target (target: 10, actual: {len(multi_paper)})")
    
    # Test 12: Paper coverage
    print("\n12. Paper Coverage")
    print("-"*80)
    
    # Get Phase 9B paper IDs
    cursor.execute("""
        SELECT id, original_filename
        FROM papers
        WHERE upload_timestamp >= '2026-10-18'
        ORDER BY upload_timestamp
    """)
    phase9b_papers = cursor.fetchall()
    
    paper_question_counts = Counter()
    for q in questions:
        for pid in q.get('paper_ids', []):
            paper_question_counts[pid] += 1
    
    print("   Questions per paper:")
    for pid, filename in phase9b_papers:
        count = paper_question_counts.get(pid, 0)
        print(f"     {filename[:30]:30s}: {count}")
        if count == 0:
            warnings.append(f"Paper {filename} has no questions")
    
    uncovered = [filename for pid, filename in phase9b_papers if paper_question_counts.get(pid, 0) == 0]
    if uncovered:
        print(f"   ⚠️  {len(uncovered)} papers without questions")
    else:
        print("   ✅ All papers covered")
    
    # Test 13: Evidence rationale
    print("\n13. Evidence Rationale")
    print("-"*80)
    
    missing_rationale = [q['id'] for q in questions if not q.get('evidence_rationale')]
    empty_rationale = [q['id'] for q in questions if len(q.get('evidence_rationale', '').strip()) < 20]
    
    if missing_rationale:
        errors.extend([f"{qid}: missing evidence_rationale" for qid in missing_rationale[:5]])
        print(f"   ❌ {len(missing_rationale)} questions missing evidence rationale")
    elif empty_rationale:
        warnings.extend([f"{qid}: evidence_rationale too brief" for qid in empty_rationale[:5]])
        print(f"   ⚠️  {len(empty_rationale)} questions with brief evidence rationale")
    else:
        print("   ✅ All questions have detailed evidence rationale")
    
    # Test 14: Expected answer keywords
    print("\n14. Expected Answer Keywords")
    print("-"*80)
    
    missing_keywords = [q['id'] for q in questions if not q.get('expected_answer_contains')]
    few_keywords = [q['id'] for q in questions if len(q.get('expected_answer_contains', [])) < 2]
    
    if missing_keywords:
        errors.extend([f"{qid}: missing expected_answer_contains" for qid in missing_keywords[:5]])
        print(f"   ❌ {len(missing_keywords)} questions missing answer keywords")
    elif few_keywords:
        warnings.extend([f"{qid}: only 1 answer keyword" for qid in few_keywords[:5]])
        print(f"   ⚠️  {len(few_keywords)} questions with <2 answer keywords")
    else:
        print("   ✅ All questions have multiple answer keywords")
    
    # Test 15: Answerable questions
    print("\n15. Answerability")
    print("-"*80)
    
    answerable = [q for q in questions if q.get('answerable', False)]
    unanswerable = [q for q in questions if not q.get('answerable', False)]
    
    print(f"   Answerable: {len(answerable)}")
    print(f"   Unanswerable: {len(unanswerable)}")
    
    if len(answerable) < 45:
        warnings.append(f"Low answerable count: {len(answerable)} (expected ~45-50)")
        print(f"   ⚠️  Low answerable count")
    else:
        print("   ✅ Good answerable ratio")
    
    # Test 16: Domain coverage
    print("\n16. Domain Coverage")
    print("-"*80)
    
    cursor.execute("""
        SELECT id, metadata
        FROM papers
        WHERE upload_timestamp >= '2026-10-18'
    """)
    
    paper_domains = {}
    for pid, metadata_json in cursor.fetchall():
        metadata = json.loads(metadata_json) if metadata_json else {}
        domain = metadata.get('domain', 'Unknown')
        paper_domains[pid] = domain
    
    domain_question_counts = Counter()
    for q in questions:
        for pid in q.get('paper_ids', []):
            if pid in paper_domains:
                domain_question_counts[paper_domains[pid]] += 1
    
    print("   Questions per domain:")
    for domain, count in sorted(domain_question_counts.items()):
        print(f"     {domain:40s}: {count}")
    
    # Check balance
    if domain_question_counts:
        max_count = max(domain_question_counts.values())
        min_count = min(domain_question_counts.values())
        if max_count > 3 * min_count:
            warnings.append(f"Imbalanced domain coverage: {max_count} vs {min_count}")
            print(f"   ⚠️  Imbalanced coverage (max: {max_count}, min: {min_count})")
        else:
            print(f"   ✅ Reasonable domain balance")
    
    conn.close()
    
    # Summary
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    
    print(f"\nDataset: {total_questions} questions")
    print(f"Papers covered: {len(paper_question_counts)}/6")
    print(f"Cross-paper questions: {len(multi_paper)}")
    print(f"Answerable questions: {len(answerable)}")
    
    if errors:
        print(f"\n❌ ERRORS: {len(errors)}")
        for err in errors[:20]:  # Show first 20 errors
            print(f"   • {err}")
        if len(errors) > 20:
            print(f"   ... and {len(errors) - 20} more errors")
    else:
        print("\n✅ NO ERRORS")
    
    if warnings:
        print(f"\n⚠️  WARNINGS: {len(warnings)}")
        for warn in warnings[:20]:  # Show first 20 warnings
            print(f"   • {warn}")
        if len(warnings) > 20:
            print(f"   ... and {len(warnings) - 20} more warnings")
    
    if not errors and not warnings:
        print("\n✅ Dataset validation PASSED - ready for evaluation")
        return True
    elif not errors:
        print("\n⚠️  Dataset validation PASSED with warnings - review recommended")
        return True
    else:
        print("\n❌ Dataset validation FAILED - errors must be fixed")
        return False

if __name__ == '__main__':
    success = validate_dataset()
    exit(0 if success else 1)
