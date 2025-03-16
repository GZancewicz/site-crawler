from bs4 import BeautifulSoup
from typing import Dict, List, Any
import re

class SEOAnalyzer:
    def __init__(self):
        self.important_meta_tags = [
            'description', 'keywords', 'robots',
            'viewport', 'og:title', 'og:description'
        ]
    
    def analyze_meta_tags(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze meta tags for SEO relevance."""
        meta_tags = {}
        for tag in soup.find_all('meta'):
            name = tag.get('name', tag.get('property', ''))
            content = tag.get('content', '')
            if name and name.lower() in self.important_meta_tags:
                meta_tags[name.lower()] = content
        
        return {
            'meta_tags_present': meta_tags,
            'missing_important_tags': [
                tag for tag in self.important_meta_tags
                if tag not in meta_tags
            ]
        }
    
    def analyze_headings(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze heading structure."""
        headings = {}
        for i in range(1, 7):
            h_tags = soup.find_all(f'h{i}')
            headings[f'h{i}'] = len(h_tags)
        
        return {
            'heading_count': headings,
            'has_h1': headings['h1'] > 0,
            'multiple_h1': headings['h1'] > 1,
            'heading_structure_issues': self._check_heading_structure(headings)
        }
    
    def analyze_images(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze image tags for alt text."""
        images = soup.find_all('img')
        images_without_alt = [img['src'] for img in images if not img.get('alt')]
        
        return {
            'total_images': len(images),
            'images_without_alt': len(images_without_alt),
            'image_alt_ratio': (len(images) - len(images_without_alt)) / len(images) if images else 1.0
        }
    
    def analyze_links(self, soup: BeautifulSoup, current_url: str) -> Dict[str, Any]:
        """Analyze internal and external links."""
        links = soup.find_all('a', href=True)
        internal_links = []
        external_links = []
        
        for link in links:
            href = link['href']
            if href.startswith('#') or not href:
                continue
            if href.startswith('http') and current_url not in href:
                external_links.append(href)
            else:
                internal_links.append(href)
        
        return {
            'total_links': len(links),
            'internal_links': len(internal_links),
            'external_links': len(external_links),
            'broken_links': []  # This would require additional HTTP requests to verify
        }
    
    def _check_heading_structure(self, headings: Dict[str, int]) -> List[str]:
        """Check for heading structure issues."""
        issues = []
        
        if headings['h1'] == 0:
            issues.append('Missing H1 tag')
        elif headings['h1'] > 1:
            issues.append('Multiple H1 tags')
        
        # Check for skipped heading levels
        last_level = 1
        for i in range(2, 7):
            if headings[f'h{i}'] > 0 and headings[f'h{last_level}'] == 0:
                issues.append(f'Skipped heading level: h{last_level} to h{i}')
            if headings[f'h{i}'] > 0:
                last_level = i
        
        return issues
    
    def analyze_title(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze page title."""
        title_tag = soup.find('title')
        title_text = title_tag.string if title_tag else None
        
        return {
            'has_title': bool(title_text),
            'title_length': len(title_text) if title_text else 0,
            'title_optimal_length': 50 <= len(title_text) <= 60 if title_text else False
        }
    
    def analyze(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Perform complete SEO analysis."""
        return {
            'meta_tags': self.analyze_meta_tags(soup),
            'headings': self.analyze_headings(soup),
            'images': self.analyze_images(soup),
            'links': self.analyze_links(soup, url),
            'title': self.analyze_title(soup)
        } 