"""
Step 1: Sentence Segmentation Module

Breaks input text into analyzable sentences and clauses.
Handles complex compound sentences for fine-grained analysis.
"""

import spacy
from typing import List
from nltk.tokenize import sent_tokenize

from .base import BaseModule
from ..models import Sentence, SentenceSegmentationResult


class SentenceSegmentationModule(BaseModule):
    """Segments text into sentences for analysis."""
    
    def __init__(self):
        super().__init__("SentenceSegmentation")
        
        # Load SpaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            self.log("SpaCy model not found. Install with: python -m spacy download en_core_web_sm", "ERROR")
            raise
    
    def _process(self, text: str) -> SentenceSegmentationResult:
        """Segment text into sentences."""
        if not text or not text.strip():
            self.log("Empty input text")
            return SentenceSegmentationResult(
                module_name=self.module_name,
                processing_time_ms=0,
                sentences=[]
            )
        
        sentences = []
        
        # Use SpaCy for primary segmentation
        doc = self.nlp(text)
        
        for i, sent in enumerate(doc.sents):
            sentence_text = sent.text.strip()
            if sentence_text:  # Skip empty sentences
                sentences.append(Sentence(
                    text=sentence_text,
                    index=i,
                    start_char=sent.start_char,
                    end_char=sent.end_char
                ))
        
        # Handle edge cases where SpaCy might miss sentences
        if len(sentences) == 0:
            self.log("SpaCy found no sentences, falling back to NLTK")
            nltk_sentences = sent_tokenize(text)
            
            char_offset = 0
            for i, sent_text in enumerate(nltk_sentences):
                sent_text = sent_text.strip()
                if sent_text:
                    start_char = text.find(sent_text, char_offset)
                    end_char = start_char + len(sent_text)
                    
                    sentences.append(Sentence(
                        text=sent_text,
                        index=i,
                        start_char=start_char,
                        end_char=end_char
                    ))
                    
                    char_offset = end_char
        
        # Handle very long sentences by splitting on conjunctions
        final_sentences = []
        for sentence in sentences:
            if len(sentence.text) > 200:  # Long sentence threshold
                sub_sentences = self._split_long_sentence(sentence)
                final_sentences.extend(sub_sentences)
            else:
                final_sentences.append(sentence)
        
        # Re-index final sentences
        for i, sentence in enumerate(final_sentences):
            sentence.index = i
        
        self.log(f"Segmented text into {len(final_sentences)} sentences")
        
        return SentenceSegmentationResult(
            module_name=self.module_name,
            processing_time_ms=0,  # Will be set by base class
            sentences=final_sentences
        )
    
    def _split_long_sentence(self, sentence: Sentence) -> List[Sentence]:
        """Split long sentences on conjunctions and clauses."""
        text = sentence.text
        
        # Split on coordinating conjunctions with proper punctuation
        split_patterns = [
            ", and ", ", but ", ", or ", ", yet ", ", so ",
            "; however,", "; therefore,", "; moreover,", "; furthermore,"
        ]
        
        parts = [text]
        for pattern in split_patterns:
            new_parts = []
            for part in parts:
                if pattern in part:
                    split_parts = part.split(pattern)
                    for i, split_part in enumerate(split_parts):
                        if i > 0:
                            # Add back the conjunction to the second part
                            split_part = pattern.strip() + " " + split_part
                        new_parts.append(split_part.strip())
                else:
                    new_parts.append(part)
            parts = new_parts
        
        # Create sentence objects for valid parts
        sub_sentences = []
        char_offset = sentence.start_char
        
        for i, part in enumerate(parts):
            part = part.strip()
            if len(part) > 10:  # Minimum meaningful length
                # Find actual position in original text
                start_pos = sentence.text.find(part.lstrip(",").strip())
                if start_pos >= 0:
                    start_char = sentence.start_char + start_pos
                    end_char = start_char + len(part)
                else:
                    start_char = char_offset
                    end_char = char_offset + len(part)
                
                sub_sentences.append(Sentence(
                    text=part,
                    index=sentence.index + i,  # Will be re-indexed later
                    start_char=start_char,
                    end_char=end_char
                ))
                
                char_offset = end_char
        
        if len(sub_sentences) > 1:
            self.log(f"Split long sentence into {len(sub_sentences)} parts")
        
        return sub_sentences if sub_sentences else [sentence]
    
    def _create_error_result(self, error_message: str) -> SentenceSegmentationResult:
        """Create error result for sentence segmentation."""
        return SentenceSegmentationResult(
            module_name=self.module_name,
            processing_time_ms=0,
            sentences=[]
        )