"""
Prompt templates for grounded Q&A and paper comparison.
"""
from typing import List, Dict


class GroundedQAPrompt:
    """
    Prompt templates for grounded research paper Q&A.
    Ensures LLM answers only from provided excerpts and doesn't fabricate information.
    """
    
    SYSTEM_PROMPT = """You are a helpful research paper assistant. Your role is to answer questions about research papers based ONLY on the provided excerpts from the paper.

CRITICAL RULES:
1. Answer using ONLY the information in the provided paper excerpts
2. Do NOT use your general knowledge or training data to fill in missing information
3. Do NOT invent facts, page numbers, or citations
4. If the excerpts don't contain enough information to answer confidently, explicitly say so
5. Be concise but informative
6. When referencing information, note which excerpt(s) support your answer (using [1], [2], etc.)
7. Do NOT fabricate or guess section names or page numbers - these will be provided separately

If you cannot answer the question from the given excerpts, respond with:
"I couldn't find sufficient information in the provided excerpts to answer this question confidently."
"""
    
    @staticmethod
    def build_user_prompt(question: str, chunks: List[Dict]) -> str:
        """
        Build the user prompt with question and retrieved chunks.
        
        Args:
            question: User's question
            chunks: Retrieved chunks with metadata
            
        Returns:
            Formatted prompt string
        """
        if not chunks:
            return f"Question: {question}\n\nNo relevant excerpts were found in the paper."
        
        # Build excerpts section
        excerpts = []
        for i, chunk in enumerate(chunks, 1):
            section = chunk.get('section', 'Unknown Section')
            page = chunk.get('page_number', '?')
            text = chunk['text'].strip()
            
            excerpt = f"[{i}] (Section: {section}, Page: {page})\n{text}"
            excerpts.append(excerpt)
        
        excerpts_text = "\n\n".join(excerpts)
        
        prompt = f"""Paper Excerpts:
{excerpts_text}

Question: {question}

Answer based only on the excerpts above. Reference excerpts using [1], [2], etc."""
        
        return prompt
    
    @staticmethod
    def build_messages(question: str, chunks: List[Dict]) -> List[Dict[str, str]]:
        """
        Build messages array for chat-based APIs.
        
        Args:
            question: User's question
            chunks: Retrieved chunks with metadata
            
        Returns:
            List of message dictionaries
        """
        return [
            {"role": "system", "content": GroundedQAPrompt.SYSTEM_PROMPT},
            {"role": "user", "content": GroundedQAPrompt.build_user_prompt(question, chunks)}
        ]
    
    @staticmethod
    def has_sufficient_context(chunks: List[Dict], min_chunks: int = 1) -> bool:
        """
        Check if we have sufficient context to attempt answering.
        
        Args:
            chunks: Retrieved chunks
            min_chunks: Minimum number of chunks required
            
        Returns:
            True if sufficient context exists
        """
        return len(chunks) >= min_chunks
    
    @staticmethod
    def get_insufficient_context_response() -> str:
        """
        Standard response when insufficient context is available.
        """
        return "I couldn't find enough relevant information in this paper to answer that question confidently."


class PromptBuilder:
    """Helper class for building various prompt configurations."""
    
    @staticmethod
    def format_chunk_preview(chunk: Dict, max_length: int = 200) -> str:
        """
        Format a chunk for preview/debugging.
        
        Args:
            chunk: Chunk dictionary
            max_length: Maximum preview length
            
        Returns:
            Formatted preview string
        """
        text = chunk['text']
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        return (
            f"Section: {chunk.get('section', 'N/A')}, "
            f"Page: {chunk.get('page_number', 'N/A')}, "
            f"Similarity: {chunk.get('similarity', 0):.2f}\n"
            f"{text}"
        )



class ComparisonExtractionPrompt:
    """
    Prompt templates for extracting structured information from research papers
    for comparison purposes.
    """
    
    SYSTEM_PROMPT = """You are a research paper analysis assistant. Your task is to extract specific structured information from a research paper.

CRITICAL RULES:
1. Use ONLY the information provided in the paper excerpts below
2. Do NOT use your general knowledge or training data
3. Do NOT infer or guess information that is not explicitly stated
4. If information is not available in the provided excerpts, you MUST respond with exactly: "Not specified in the paper"
5. Be concise but preserve important technical details
6. Extract factual information only

You will extract exactly 4 fields:
- Method: The methodology, model, algorithm, or approach used in the paper
- Dataset: The dataset(s), benchmark(s), or data sources used for experiments
- Metric/Result: Key evaluation metrics or main results reported
- Limitation: Limitations explicitly stated or clearly identified in the paper

Return your response as a valid JSON object with exactly these fields:
{
  "method": "...",
  "dataset": "...",
  "metric_result": "...",
  "limitation": "..."
}

If any field cannot be determined from the provided content, use "Not specified in the paper" as the value for that field.
"""
    
    @staticmethod
    def build_extraction_prompt(paper_content: str, paper_filename: str) -> str:
        """
        Build the extraction prompt for a single paper.
        
        Args:
            paper_content: Concatenated relevant paper excerpts
            paper_filename: Name of the paper file
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""Paper: {paper_filename}

Paper Content:
{paper_content}

---

Extract the following information from this paper:

1. Method: What methodology, model, algorithm, or approach does the paper use?
2. Dataset: What dataset(s), benchmark(s), or data sources are used?
3. Metric/Result: What are the key evaluation metrics or main results?
4. Limitation: What limitations are explicitly stated in the paper?

Remember:
- Use ONLY information from the paper content above
- If information is not available, respond with "Not specified in the paper"
- Return valid JSON with fields: method, dataset, metric_result, limitation

Response:"""
        
        return prompt
    
    @staticmethod
    def build_extraction_messages(paper_content: str, paper_filename: str) -> List[Dict[str, str]]:
        """
        Build messages array for chat-based APIs.
        
        Args:
            paper_content: Concatenated relevant paper excerpts
            paper_filename: Name of the paper file
            
        Returns:
            List of message dictionaries
        """
        return [
            {"role": "system", "content": ComparisonExtractionPrompt.SYSTEM_PROMPT},
            {"role": "user", "content": ComparisonExtractionPrompt.build_extraction_prompt(
                paper_content, paper_filename
            )}
        ]
    
    @staticmethod
    def validate_extraction_response(response: str) -> bool:
        """
        Validate that response looks like valid JSON.
        
        Args:
            response: LLM response string
            
        Returns:
            True if response appears valid
        """
        import json
        try:
            data = json.loads(response)
            required_fields = ["method", "dataset", "metric_result", "limitation"]
            return all(field in data for field in required_fields)
        except (json.JSONDecodeError, TypeError):
            return False



class GapAnalysisPrompt:
    """
    Prompt templates for analyzing research gaps and contradictions
    from structured paper comparison data.
    """
    
    SYSTEM_PROMPT = """You are a research gap analysis assistant. Your task is to identify possible research gaps or contradictions from structured comparison data of multiple research papers.

CRITICAL RULES:
1. Analyze ONLY the provided structured comparison data (methods, datasets, results, limitations)
2. Do NOT use outside knowledge or make claims about the broader research field
3. Do NOT claim that something has never been studied - only that it's not present in the compared papers
4. Identify 0-3 possible research gaps or contradictions based on the evidence
5. Each gap must be supported by specific observations from the comparison data
6. Distinguish clearly between observations (facts from the data) and possibilities (research opportunities)
7. Use cautious language: "suggests", "appears", "based on the compared papers", "possible opportunity"
8. Do NOT force gaps if the evidence is weak - it's acceptable to return 0 gaps
9. Prefer specific, evidence-based suggestions over generic statements
10. Be concise but clear

GAP TYPES TO CONSIDER:
- Dataset gaps: Limited or similar datasets across papers
- Methodological gaps: Unexplored methodological variations or comparisons
- Evaluation gaps: Missing metrics, inconsistent evaluation approaches
- Contradictions: Conflicting results or claims between papers
- Limitation-derived gaps: Common limitations suggesting research opportunities

OUTPUT FORMAT:
Return a valid JSON array with 0-3 gap objects. Each gap must have:
{
  "title": "Brief title (max 200 chars)",
  "description": "Detailed description of the gap (max 1000 chars)",
  "basis": "Specific evidence from the comparison supporting this gap (max 500 chars)"
}

If no strong gaps can be identified, return an empty array: []

LANGUAGE GUIDELINES:
- AVOID: "No researchers have studied X", "This has never been explored"
- PREFER: "The compared papers do not evaluate X", "This suggests a possible opportunity to investigate Y"
- AVOID: Definitive claims about the entire research field
- PREFER: Observations limited to the provided papers

Return ONLY valid JSON, no additional text."""
    
    @staticmethod
    def build_analysis_messages(comparison_data: List[Dict]) -> List[Dict[str, str]]:
        """
        Build messages for gap analysis from structured comparison data.
        
        Args:
            comparison_data: List of PaperComparisonResult dictionaries
            
        Returns:
            List of message dictionaries for LLM
        """
        # Format comparison data into readable structure
        papers_text = []
        for i, paper in enumerate(comparison_data, 1):
            paper_text = f"""Paper {i}: {paper.get('filename', 'Unknown')}
- Method: {paper.get('method', 'Not specified')}
- Dataset: {paper.get('dataset', 'Not specified')}
- Metric/Result: {paper.get('metric_result', 'Not specified')}
- Limitation: {paper.get('limitation', 'Not specified')}"""
            papers_text.append(paper_text)
        
        comparison_text = "\n\n".join(papers_text)
        
        user_prompt = f"""Analyze the following {len(comparison_data)} research papers for possible research gaps or contradictions.

STRUCTURED COMPARISON DATA:
{comparison_text}

Based ONLY on the information above, identify 0-3 possible research gaps or contradictions.
Return a JSON array of gap objects, or an empty array [] if no strong gaps can be identified.

Remember:
- Each gap must be supported by specific evidence from the comparison
- Use cautious language (suggests, appears, possible)
- Do not claim knowledge about the broader research field
- It's acceptable to return fewer than 3 gaps or even 0 gaps"""
        
        return [
            {"role": "system", "content": GapAnalysisPrompt.SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
    
    @staticmethod
    def validate_gap_format(gap: Dict) -> bool:
        """
        Validate that a gap has required fields.
        
        Args:
            gap: Gap dictionary
            
        Returns:
            True if valid format
        """
        required_fields = ["title", "description", "basis"]
        return all(field in gap and isinstance(gap[field], str) and gap[field].strip() 
                   for field in required_fields)
