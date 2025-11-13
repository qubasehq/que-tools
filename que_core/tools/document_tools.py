"""
Document Tools - Consolidated document processing and text analysis for AI agents
Provides unified document handling and intelligent text operations.
"""
from typing import Any, Dict, List
import os
import re
import json
import tempfile

def document_processor(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Universal document processor - replaces summarize_text, extract_text_from_pdf, analyze_sentiment, spell_check, search_text, convert_doc_format
    
    Args:
        action (str): Action to perform - 'summarize', 'extract_pdf', 'convert', 'spell_check', 'search_text', 'analyze_sentiment'
        text (str): Text to process (for text-based actions)
        file (str): File path to process (for file-based actions)
        output_format (str): Output format for conversion (optional)
        max_sentences (int): Maximum sentences for summary (optional)
        query (str): Search query for text search (optional)
        
    Returns:
        Dict with processing result
    """
    if not args or "action" not in args:
        return {"success": False, "result": None, "error": "Missing required argument: action"}
    
    action = args["action"]
    
    try:
        if action == "summarize":
            return _summarize_text_impl(args)
        elif action == "extract_pdf":
            return _extract_pdf_impl(args)
        elif action == "convert":
            return _convert_document_impl(args)
        elif action == "spell_check":
            return _spell_check_impl(args)
        elif action == "search_text":
            return _search_text_impl(args)
        elif action == "analyze_sentiment":
            return _analyze_sentiment_impl(args)
        else:
            return {
                "success": False,
                "result": None,
                "error": f"Unknown action: {action}. Use: summarize, extract_pdf, convert, spell_check, search_text, analyze_sentiment"
            }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Document processing failed: {str(e)}"}

def text_analyzer(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Smart text operations - replaces analyze_sentiment, spell_check, translate_text, search_text
    
    Args:
        action (str): Action to perform - 'sentiment', 'spell_check', 'translate', 'search', 'stats', 'extract_keywords'
        text (str): Text to analyze
        to (str): Target language for translation (optional)
        query (str): Search query (optional)
        
    Returns:
        Dict with analysis result
    """
    if not args or "action" not in args:
        return {"success": False, "result": None, "error": "Missing required argument: action"}
    
    action = args["action"]
    
    try:
        if action == "sentiment":
            return _analyze_sentiment_impl(args)
        elif action == "spell_check":
            return _spell_check_impl(args)
        elif action == "translate":
            return _translate_text_impl(args)
        elif action == "search":
            return _search_text_impl(args)
        elif action == "stats":
            return _text_statistics_impl(args)
        elif action == "extract_keywords":
            return _extract_keywords_impl(args)
        else:
            return {
                "success": False,
                "result": None,
                "error": f"Unknown action: {action}. Use: sentiment, spell_check, translate, search, stats, extract_keywords"
            }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Text analysis failed: {str(e)}"}

# Document Processor Implementation Helpers
def _summarize_text_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Text summarization implementation"""
    try:
        text = args.get("text")
        if not text:
            return {"success": False, "result": None, "error": "Missing required argument: text"}
        
        max_sentences = args.get("max_sentences", 3)
        
        # Simple extractive summarization
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= max_sentences:
            summary = text
            compression_ratio = 1.0
        else:
            # Score sentences by word frequency
            words = re.findall(r'\w+', text.lower())
            word_freq = {}
            for word in words:
                if len(word) > 3:  # Skip short words
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Score sentences
            sentence_scores = []
            for i, sentence in enumerate(sentences):
                score = 0
                sentence_words = re.findall(r'\w+', sentence.lower())
                for word in sentence_words:
                    if word in word_freq:
                        score += word_freq[word]
                sentence_scores.append((score, i, sentence))
            
            # Get top sentences
            sentence_scores.sort(reverse=True)
            top_sentences = sentence_scores[:max_sentences]
            top_sentences.sort(key=lambda x: x[1])  # Sort by original order
            
            summary = '. '.join([s[2] for s in top_sentences]) + '.'
            compression_ratio = len(summary) / len(text)
        
        return {
            "success": True,
            "result": {
                "summary": summary,
                "original_length": len(text),
                "summary_length": len(summary),
                "compression_ratio": round(compression_ratio, 3),
                "sentences_selected": min(len(sentences), max_sentences),
                "total_sentences": len(sentences),
                "method": "extractive_summarization"
            },
            "error": None
        }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Text summarization failed: {str(e)}"}

def _extract_pdf_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """PDF text extraction implementation"""
    try:
        file_path = args.get("file")
        if not file_path:
            return {"success": False, "result": None, "error": "Missing required argument: file"}
        
        if not os.path.exists(file_path):
            return {"success": False, "result": None, "error": f"File not found: {file_path}"}
        
        # Try PyPDF2 first
        try:
            import PyPDF2
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                
                return {
                    "success": True,
                    "result": {
                        "text": text.strip(),
                        "pages": len(pdf_reader.pages),
                        "file_path": file_path,
                        "text_length": len(text),
                        "word_count": len(text.split()),
                        "method": "pypdf2"
                    },
                    "error": None
                }
        
        except ImportError:
            # Try pdfplumber as fallback
            try:
                import pdfplumber
                
                text = ""
                page_count = 0
                
                with pdfplumber.open(file_path) as pdf:
                    for page_num, page in enumerate(pdf.pages):
                        page_text = page.extract_text()
                        if page_text:
                            text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                        page_count += 1
                
                return {
                    "success": True,
                    "result": {
                        "text": text.strip(),
                        "pages": page_count,
                        "file_path": file_path,
                        "text_length": len(text),
                        "word_count": len(text.split()),
                        "method": "pdfplumber"
                    },
                    "error": None
                }
            
            except ImportError:
                return {"success": False, "result": None, "error": "PDF extraction requires PyPDF2 or pdfplumber (pip install PyPDF2 pdfplumber)"}
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"PDF extraction failed: {str(e)}"}

def _convert_document_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Document conversion implementation"""
    try:
        file_path = args.get("file")
        output_format = args.get("output_format", "txt")
        
        if not file_path:
            return {"success": False, "result": None, "error": "Missing required argument: file"}
        
        if not os.path.exists(file_path):
            return {"success": False, "result": None, "error": f"File not found: {file_path}"}
        
        # Basic document conversion (placeholder implementation)
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == ".pdf" and output_format == "txt":
            # Convert PDF to text
            pdf_result = _extract_pdf_impl(args)
            if pdf_result["success"]:
                output_path = args.get("output_path")
                if not output_path:
                    base_name = os.path.splitext(os.path.basename(file_path))[0]
                    output_path = os.path.join(tempfile.gettempdir(), f"{base_name}.txt")
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(pdf_result["result"]["text"])
                
                return {
                    "success": True,
                    "result": {
                        "input_file": file_path,
                        "output_file": output_path,
                        "input_format": "pdf",
                        "output_format": "txt",
                        "file_size": os.path.getsize(output_path),
                        "method": "pdf_to_text"
                    },
                    "error": None
                }
            else:
                return pdf_result
        
        else:
            return {
                "success": False,
                "result": None,
                "error": f"Conversion from {file_ext} to {output_format} not yet supported"
            }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Document conversion failed: {str(e)}"}

def _spell_check_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Spell check implementation"""
    try:
        text = args.get("text")
        if not text:
            return {"success": False, "result": None, "error": "Missing required argument: text"}
        
        # Try pyspellchecker
        try:
            from spellchecker import SpellChecker
            
            spell = SpellChecker()
            words = text.split()
            
            # Find misspelled words
            misspelled = spell.unknown(words)
            
            corrections = {}
            for word in misspelled:
                # Get the most likely correction
                correction = spell.correction(word)
                if correction != word:
                    corrections[word] = correction
            
            return {
                "success": True,
                "result": {
                    "text": text,
                    "total_words": len(words),
                    "misspelled_count": len(misspelled),
                    "misspelled_words": list(misspelled),
                    "corrections": corrections,
                    "accuracy": round((len(words) - len(misspelled)) / len(words) * 100, 2),
                    "method": "pyspellchecker"
                },
                "error": None
            }
        
        except ImportError:
            # Basic spell check using common patterns
            common_errors = {
                "teh": "the",
                "adn": "and",
                "recieve": "receive",
                "seperate": "separate",
                "definately": "definitely",
                "occured": "occurred"
            }
            
            words = text.split()
            corrections = {}
            
            for word in words:
                clean_word = re.sub(r'[^\w]', '', word.lower())
                if clean_word in common_errors:
                    corrections[word] = common_errors[clean_word]
            
            return {
                "success": True,
                "result": {
                    "text": text,
                    "total_words": len(words),
                    "corrections": corrections,
                    "method": "basic_patterns"
                },
                "error": None
            }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Spell check failed: {str(e)}"}

def _search_text_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Text search implementation"""
    try:
        text = args.get("text")
        query = args.get("query")
        
        if not text:
            return {"success": False, "result": None, "error": "Missing required argument: text"}
        
        if not query:
            return {"success": False, "result": None, "error": "Missing required argument: query"}
        
        case_sensitive = args.get("case_sensitive", False)
        whole_words = args.get("whole_words", False)
        
        # Prepare search pattern
        if whole_words:
            pattern = r'\b' + re.escape(query) + r'\b'
        else:
            pattern = re.escape(query)
        
        flags = 0 if case_sensitive else re.IGNORECASE
        
        # Find all matches
        matches = []
        for match in re.finditer(pattern, text, flags):
            start = match.start()
            end = match.end()
            
            # Get context around match
            context_start = max(0, start - 50)
            context_end = min(len(text), end + 50)
            context = text[context_start:context_end]
            
            matches.append({
                "match": match.group(),
                "start": start,
                "end": end,
                "context": context,
                "line_number": text[:start].count('\n') + 1
            })
        
        return {
            "success": True,
            "result": {
                "query": query,
                "matches": matches,
                "match_count": len(matches),
                "case_sensitive": case_sensitive,
                "whole_words": whole_words,
                "text_length": len(text),
                "method": "regex_search"
            },
            "error": None
        }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Text search failed: {str(e)}"}

def _analyze_sentiment_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Sentiment analysis implementation"""
    try:
        text = args.get("text")
        if not text:
            return {"success": False, "result": None, "error": "Missing required argument: text"}
        
        # Try TextBlob for sentiment analysis
        try:
            from textblob import TextBlob
            
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity  # -1 to 1
            subjectivity = blob.sentiment.subjectivity  # 0 to 1
            
            # Classify sentiment
            if polarity > 0.1:
                sentiment = "positive"
            elif polarity < -0.1:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            
            # Classify subjectivity
            if subjectivity > 0.5:
                objectivity = "subjective"
            else:
                objectivity = "objective"
            
            return {
                "success": True,
                "result": {
                    "text": text,
                    "sentiment": sentiment,
                    "polarity": round(polarity, 3),
                    "subjectivity": round(subjectivity, 3),
                    "objectivity": objectivity,
                    "confidence": round(abs(polarity), 3),
                    "method": "textblob"
                },
                "error": None
            }
        
        except ImportError:
            # Basic sentiment analysis using word lists
            positive_words = ["good", "great", "excellent", "amazing", "wonderful", "fantastic", "love", "like", "happy", "joy"]
            negative_words = ["bad", "terrible", "awful", "horrible", "hate", "dislike", "sad", "angry", "disappointed", "frustrated"]
            
            words = re.findall(r'\w+', text.lower())
            
            positive_count = sum(1 for word in words if word in positive_words)
            negative_count = sum(1 for word in words if word in negative_words)
            
            if positive_count > negative_count:
                sentiment = "positive"
                polarity = 0.5
            elif negative_count > positive_count:
                sentiment = "negative"
                polarity = -0.5
            else:
                sentiment = "neutral"
                polarity = 0.0
            
            return {
                "success": True,
                "result": {
                    "text": text,
                    "sentiment": sentiment,
                    "polarity": polarity,
                    "positive_words": positive_count,
                    "negative_words": negative_count,
                    "method": "word_list"
                },
                "error": None
            }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Sentiment analysis failed: {str(e)}"}

# Text Analyzer Implementation Helpers
def _translate_text_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Text translation implementation"""
    try:
        text = args.get("text")
        to_lang = args.get("to", "en")
        
        if not text:
            return {"success": False, "result": None, "error": "Missing required argument: text"}
        
        # Translation requires external services or libraries
        return {
            "success": False,
            "result": None,
            "error": "Text translation requires additional setup (Google Translate API, Azure Translator, or googletrans library)"
        }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Text translation failed: {str(e)}"}

def _text_statistics_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Text statistics implementation"""
    try:
        text = args.get("text")
        if not text:
            return {"success": False, "result": None, "error": "Missing required argument: text"}
        
        # Calculate various text statistics
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        # Character counts
        char_count = len(text)
        char_count_no_spaces = len(text.replace(' ', ''))
        
        # Word statistics
        word_count = len(words)
        unique_words = len(set(word.lower() for word in words))
        
        # Average lengths
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        avg_sentence_length = word_count / len(sentences) if sentences else 0
        
        # Reading time (average 200 words per minute)
        reading_time_minutes = word_count / 200
        
        return {
            "success": True,
            "result": {
                "text_length": char_count,
                "text_length_no_spaces": char_count_no_spaces,
                "word_count": word_count,
                "unique_words": unique_words,
                "sentence_count": len(sentences),
                "paragraph_count": len(paragraphs),
                "avg_word_length": round(avg_word_length, 2),
                "avg_sentence_length": round(avg_sentence_length, 2),
                "reading_time_minutes": round(reading_time_minutes, 2),
                "lexical_diversity": round(unique_words / word_count, 3) if word_count > 0 else 0,
                "method": "text_statistics"
            },
            "error": None
        }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Text statistics failed: {str(e)}"}

def _extract_keywords_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Keyword extraction implementation"""
    try:
        text = args.get("text")
        if not text:
            return {"success": False, "result": None, "error": "Missing required argument: text"}
        
        max_keywords = args.get("max_keywords", 10)
        
        # Simple keyword extraction using word frequency
        words = re.findall(r'\w+', text.lower())
        
        # Filter out common stop words
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by",
            "is", "are", "was", "were", "be", "been", "have", "has", "had", "do", "does", "did",
            "will", "would", "could", "should", "may", "might", "can", "this", "that", "these", "those"
        }
        
        # Count word frequencies
        word_freq = {}
        for word in words:
            if len(word) > 3 and word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:max_keywords]
        
        return {
            "success": True,
            "result": {
                "keywords": [{"word": word, "frequency": freq} for word, freq in keywords],
                "total_unique_words": len(word_freq),
                "total_words": len(words),
                "method": "frequency_analysis"
            },
            "error": None
        }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Keyword extraction failed: {str(e)}"}

# Legacy function aliases for backward compatibility
def summarize_text(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use document_processor instead"""
    return document_processor(args={"action": "summarize", **(args or {})})

def extract_text_from_pdf(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use document_processor instead"""
    return document_processor(args={"action": "extract_pdf", **(args or {})})

def convert_doc_format(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use document_processor instead"""
    return document_processor(args={"action": "convert", **(args or {})})

def analyze_sentiment(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use text_analyzer instead"""
    return text_analyzer(args={"action": "sentiment", **(args or {})})

def spell_check(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use text_analyzer instead"""
    return text_analyzer(args={"action": "spell_check", **(args or {})})

def translate_text(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use text_analyzer instead"""
    return text_analyzer(args={"action": "translate", **(args or {})})

def search_text(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use text_analyzer instead"""
    return text_analyzer(args={"action": "search", **(args or {})})

def generate_report(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - not yet implemented"""
    return {"success": False, "result": None, "error": "Report generation not yet implemented"}
