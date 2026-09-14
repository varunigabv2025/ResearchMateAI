"""
Tests for prompt templates.
"""
import pytest
from app.services.prompts import GroundedQAPrompt


class TestGroundedQAPrompt:
    """Tests for grounded Q&A prompts."""
    
    def test_build_user_prompt_with_chunks(self):
        """Test building user prompt with chunks."""
        question = "What methodology was used?"
        chunks = [
            {
                'text': 'We used a transformer architecture.',
                'page_number': 7,
                'section': 'Methodology'
            },
            {
                'text': 'The model was trained on 100k examples.',
                'page_number': 9,
                'section': 'Experiments'
            }
        ]
        
        prompt = GroundedQAPrompt.build_user_prompt(question, chunks)
        
        assert question in prompt
        assert '[1]' in prompt
        assert '[2]' in prompt
        assert 'Methodology' in prompt
        assert 'Page: 7' in prompt
        assert 'transformer architecture' in prompt
    
    def test_build_user_prompt_empty_chunks(self):
        """Test building prompt with no chunks."""
        question = "What is this about?"
        chunks = []
        
        prompt = GroundedQAPrompt.build_user_prompt(question, chunks)
        
        assert question in prompt
        assert "No relevant excerpts were found" in prompt
    
    def test_build_messages(self):
        """Test building messages for chat API."""
        question = "What is the main finding?"
        chunks = [
            {
                'text': 'Our main finding is X.',
                'page_number': 5,
                'section': 'Results'
            }
        ]
        
        messages = GroundedQAPrompt.build_messages(question, chunks)
        
        assert len(messages) == 2
        assert messages[0]['role'] == 'system'
        assert messages[1]['role'] == 'user'
        assert 'ONLY' in messages[0]['content']  # Emphasis on grounding
        assert question in messages[1]['content']
    
    def test_has_sufficient_context(self):
        """Test checking for sufficient context."""
        # With chunks
        chunks = [{'text': 'some text'}]
        assert GroundedQAPrompt.has_sufficient_context(chunks, min_chunks=1) is True
        
        # Without chunks
        assert GroundedQAPrompt.has_sufficient_context([], min_chunks=1) is False
        
        # Below threshold
        assert GroundedQAPrompt.has_sufficient_context(chunks, min_chunks=2) is False
    
    def test_get_insufficient_context_response(self):
        """Test getting insufficient context response."""
        response = GroundedQAPrompt.get_insufficient_context_response()
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert "couldn't find" in response.lower() or "insufficient" in response.lower()
    
    def test_system_prompt_emphasizes_grounding(self):
        """Test that system prompt emphasizes grounding rules."""
        system_prompt = GroundedQAPrompt.SYSTEM_PROMPT
        
        # Check for key grounding instructions
        assert "ONLY" in system_prompt
        assert "provided excerpts" in system_prompt or "provided paper" in system_prompt
        assert "do not" in system_prompt.lower() or "don't" in system_prompt.lower()
        assert "invent" in system_prompt.lower() or "fabricate" in system_prompt.lower()
