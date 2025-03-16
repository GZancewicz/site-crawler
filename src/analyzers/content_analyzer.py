from bs4 import BeautifulSoup
from typing import Dict, Any, List
import re
from collections import Counter

class ContentAnalyzer:
    def __init__(self):
        self.min_word_count = 300
        self.max_keyword_density = 0.03
        self.stop_words = {
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have',
            'i', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you',
            'do', 'at', 'this', 'but', 'his', 'by', 'from', 'they',
            'we', 'say', 'her', 'she', 'or', 'an', 'will', 'my', 'one',
            'all', 'would', 'there', 'their', 'what', 'so', 'up', 'out',
            'if', 'about', 'who', 'get', 'which', 'go', 'me'
        }
    
    def extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract main text content from the page."""
        # Remove script and style elements
        for script in soup(['script', 'style', 'nav', 'header', 'footer']):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        # Break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split('  '))
        # Drop blank lines
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def analyze_readability(self, text: str) -> Dict[str, Any]:
        """Analyze text readability using various metrics."""
        sentences = self._split_into_sentences(text)
        words = self._split_into_words(text)
        syllables = sum(self._count_syllables(word) for word in words)
        
        # Calculate metrics
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        avg_syllables_per_word = syllables / len(words) if words else 0
        
        # Flesch Reading Ease score
        flesch_score = 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables_per_word
        
        return {
            'flesch_reading_ease': round(flesch_score, 2),
            'avg_sentence_length': round(avg_sentence_length, 2),
            'avg_syllables_per_word': round(avg_syllables_per_word, 2),
            'readability_level': self._get_readability_level(flesch_score)
        }
    
    def analyze_keyword_density(self, text: str) -> Dict[str, Any]:
        """Analyze keyword density and distribution."""
        words = self._split_into_words(text.lower())
        # Remove stop words
        words = [word for word in words if word not in self.stop_words]
        
        # Count word frequencies
        word_freq = Counter(words)
        total_words = len(words)
        
        # Get top keywords and their densities
        top_keywords = word_freq.most_common(10)
        keyword_densities = {
            word: count/total_words
            for word, count in top_keywords
        }
        
        return {
            'top_keywords': top_keywords,
            'keyword_densities': keyword_densities,
            'keyword_density_issues': [
                word for word, density in keyword_densities.items()
                if density > self.max_keyword_density
            ]
        }
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        return re.split(r'[.!?]+', text)
    
    def _split_into_words(self, text: str) -> List[str]:
        """Split text into words."""
        return re.findall(r'\b\w+\b', text)
    
    def _count_syllables(self, word: str) -> int:
        """Count the number of syllables in a word."""
        word = word.lower()
        count = 0
        vowels = 'aeiouy'
        if word[0] in vowels:
            count += 1
        for index in range(1, len(word)):
            if word[index] in vowels and word[index - 1] not in vowels:
                count += 1
        if word.endswith('e'):
            count -= 1
        if count == 0:
            count = 1
        return count
    
    def _get_readability_level(self, flesch_score: float) -> str:
        """Convert Flesch score to readability level."""
        if flesch_score >= 90:
            return 'Very Easy'
        elif flesch_score >= 80:
            return 'Easy'
        elif flesch_score >= 70:
            return 'Fairly Easy'
        elif flesch_score >= 60:
            return 'Standard'
        elif flesch_score >= 50:
            return 'Fairly Difficult'
        elif flesch_score >= 30:
            return 'Difficult'
        else:
            return 'Very Difficult'
    
    def analyze_content_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze content structure and formatting."""
        paragraphs = soup.find_all('p')
        lists = soup.find_all(['ul', 'ol'])
        
        return {
            'paragraph_count': len(paragraphs),
            'list_count': len(lists),
            'avg_paragraph_length': sum(len(p.get_text().split()) for p in paragraphs) / len(paragraphs) if paragraphs else 0,
            'has_lists': bool(lists),
            'structure_score': self._calculate_structure_score(paragraphs, lists)
        }
    
    def _calculate_structure_score(self, paragraphs: List, lists: List) -> float:
        """Calculate a score for content structure."""
        score = 0.0
        
        # Good number of paragraphs (5-15)
        if 5 <= len(paragraphs) <= 15:
            score += 0.4
        elif len(paragraphs) > 0:
            score += 0.2
        
        # Presence of lists
        if lists:
            score += 0.3
        
        # Average paragraph length (50-200 words)
        avg_length = sum(len(p.get_text().split()) for p in paragraphs) / len(paragraphs) if paragraphs else 0
        if 50 <= avg_length <= 200:
            score += 0.3
        elif avg_length > 0:
            score += 0.1
        
        return score
    
    def analyze(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Perform complete content analysis."""
        text_content = self.extract_text_content(soup)
        
        return {
            'readability': self.analyze_readability(text_content),
            'keyword_analysis': self.analyze_keyword_density(text_content),
            'content_structure': self.analyze_content_structure(soup),
            'word_count': len(self._split_into_words(text_content)),
            'sufficient_content': len(self._split_into_words(text_content)) >= self.min_word_count
        } 