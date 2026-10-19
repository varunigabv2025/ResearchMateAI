"""
Phase 9A Dataset Validation Script
Validates that the expanded 25-question dataset meets all requirements.
"""
import json
from pathlib import Path

def validate_dataset():
    """Validate Phase 9A dataset structure and content."""
    
    dataset_path = Path(__file__).parent / "dataset_phase9a.json"
    original_path = Path(__file__).parent / "dataset.json"
    
    print("="*80)
    print("PHASE 9A DATASET VALIDATION")
    print("="*80)
    
    # Load datasets
    with open(dataset_path) as f:
        phase9a = json.load(f)
    
    with open(original_path) as f:
        original = json.load(f)
    
    errors = []
    warnings = []
    
    # Test 1: Question count
    print("\n1. Question Count Validation")
    total_questions = len(phase9a['questions'])
    original_questions = sum(1 for q in phase9a['questions'] if q.get('phase') == 'original')
    new_questions = sum(1 for q in phase9a['questions'] if q.get('phase') == 'phase9a')
    
    print(f"   Total questions: {total_questions}")
    print(f"   Original questions: {original_questions}")
    print(f"   New questions: {new_questions}")
    
    if total_questions != 25:
        errors.append(f"Expected 25 total questions, got {total_questions}")
    else:
        print("   ✅ Correct total count (25)")
    
    if original_questions != 10:
        errors.append(f"Expected 10 original questions, got {original_questions}")
    else:
        print("   ✅ Correct original count (10)")
    
    if new_questions != 15:
        errors.append(f"Expected 15 new questions, got {new_questions}")
    else:
        print("   ✅ Correct new count (15)")
    
    # Test 2: Original questions unchanged
    print("\n2. Original Questions Integrity")
    original_questions_data = {q['id']: q for q in original['questions']}
    phase9a_original = {q['id']: q for q in phase9a['questions'] if q.get('phase') == 'original'}
    
    for qid in ['q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8', 'q9', 'q10']:
        if qid not in phase9a_original:
            errors.append(f"Original question {qid} missing from Phase 9A dataset")
            continue
        
        orig = original_questions_data[qid]
        new = phase9a_original[qid]
        
        # Check critical fields
        if orig['question'] != new['question']:
            errors.append(f"{qid}: Question text modified")
        if orig['category'] != new['category']:
            warnings.append(f"{qid}: Category modified")
        if orig['relevant_pages'] != new['relevant_pages']:
            errors.append(f"{qid}: Relevant pages modified")
        if orig['answerable'] != new['answerable']:
            errors.append(f"{qid}: Answerability modified")
    
    if not any(qid in err for err in errors for qid in ['q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8', 'q9', 'q10']):
        print("   ✅ Original questions preserved")
    
    # Test 3: Question ID uniqueness
    print("\n3. Question ID Uniqueness")
    question_ids = [q['id'] for q in phase9a['questions']]
    if len(question_ids) != len(set(question_ids)):
        errors.append("Duplicate question IDs found")
        duplicates = [qid for qid in question_ids if question_ids.count(qid) > 1]
        print(f"   ❌ Duplicates: {set(duplicates)}")
    else:
        print("   ✅ All question IDs unique")
    
    # Test 4: Required fields present
    print("\n4. Required Fields")
    required_fields = ['id', 'question', 'category', 'difficulty', 'relevant_pages', 'answerable', 'phase']
    missing_fields = []
    
    for q in phase9a['questions']:
        for field in required_fields:
            if field not in q:
                missing_fields.append(f"{q['id']}: missing '{field}'")
    
    if missing_fields:
        errors.extend(missing_fields)
        print(f"   ❌ Missing fields: {len(missing_fields)}")
    else:
        print("   ✅ All required fields present")
    
    # Test 5: Valid categories
    print("\n5. Question Categories")
    categories = [q['category'] for q in phase9a['questions']]
    category_counts = {}
    for cat in categories:
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    print("   Category distribution:")
    for cat, count in sorted(category_counts.items()):
        print(f"     {cat}: {count}")
    
    # Test 6: Valid difficulty levels
    print("\n6. Difficulty Levels")
    difficulties = [q['difficulty'] for q in phase9a['questions']]
    valid_difficulties = ['easy', 'medium', 'hard']
    
    invalid = [d for d in difficulties if d not in valid_difficulties]
    if invalid:
        errors.append(f"Invalid difficulty levels: {set(invalid)}")
    
    diff_counts = {d: difficulties.count(d) for d in valid_difficulties if d in difficulties}
    print("   Difficulty distribution:")
    for diff, count in diff_counts.items():
        print(f"     {diff}: {count}")
    
    if not invalid:
        print("   ✅ All difficulty levels valid")
    
    # Test 7: Relevant pages
    print("\n7. Relevant Pages")
    for q in phase9a['questions']:
        if q['answerable'] and not q['relevant_pages']:
            warnings.append(f"{q['id']}: Answerable but no relevant pages specified")
        
        invalid_pages = [p for p in q['relevant_pages'] if p < 1 or p > 6]
        if invalid_pages:
            errors.append(f"{q['id']}: Invalid page numbers {invalid_pages} (paper has 6 pages)")
    
    if not any('Invalid page' in err for err in errors):
        print("   ✅ All page numbers valid (1-6)")
    
    # Test 8: Paper ID consistency
    print("\n8. Paper ID")
    if phase9a.get('paper_id') == original.get('paper_id'):
        print(f"   ✅ Paper ID consistent: {phase9a.get('paper_id')}")
    else:
        errors.append("Paper ID mismatch between original and Phase 9A dataset")
    
    # Test 9: New question quality
    print("\n9. New Question Quality")
    new_qs = [q for q in phase9a['questions'] if q.get('phase') == 'phase9a']
    
    for q in new_qs:
        if not q.get('notes'):
            warnings.append(f"{q['id']}: Missing notes/explanation")
        if not q.get('expected_answer_contains'):
            warnings.append(f"{q['id']}: Missing expected answer keywords")
    
    print(f"   ✅ {len(new_qs)} new questions created")
    
    # Summary
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    
    if errors:
        print(f"\n❌ ERRORS FOUND: {len(errors)}")
        for err in errors:
            print(f"   • {err}")
    else:
        print("\n✅ NO ERRORS")
    
    if warnings:
        print(f"\n⚠️  WARNINGS: {len(warnings)}")
        for warn in warnings:
            print(f"   • {warn}")
    
    if not errors and not warnings:
        print("\n✅ Dataset validation PASSED - ready for evaluation")
        return True
    elif not errors:
        print("\n⚠️  Dataset validation PASSED with warnings")
        return True
    else:
        print("\n❌ Dataset validation FAILED")
        return False

if __name__ == '__main__':
    success = validate_dataset()
    exit(0 if success else 1)
