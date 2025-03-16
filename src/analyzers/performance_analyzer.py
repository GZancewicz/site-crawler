from typing import Dict, Any
import re
from bs4 import BeautifulSoup

class PerformanceAnalyzer:
    def __init__(self):
        self.size_thresholds = {
            'html': 100 * 1024,  # 100KB
            'total': 3 * 1024 * 1024  # 3MB
        }
    
    def analyze_load_time(self, load_time: float) -> Dict[str, Any]:
        """Analyze page load time."""
        return {
            'load_time_seconds': load_time,
            'load_time_acceptable': load_time < 3.0,  # Google's recommended threshold
            'performance_score': self._calculate_performance_score(load_time)
        }
    
    def analyze_page_size(self, content: str) -> Dict[str, Any]:
        """Analyze page size and content."""
        html_size = len(content.encode('utf-8'))
        
        return {
            'html_size_bytes': html_size,
            'html_size_acceptable': html_size <= self.size_thresholds['html'],
            'estimated_total_size': self._estimate_total_page_size(content)
        }
    
    def _calculate_performance_score(self, load_time: float) -> float:
        """Calculate a performance score based on load time."""
        if load_time <= 1.0:
            return 1.0
        elif load_time <= 2.5:
            return 0.8
        elif load_time <= 4.0:
            return 0.6
        elif load_time <= 6.0:
            return 0.4
        else:
            return 0.2
    
    def _estimate_total_page_size(self, content: str) -> Dict[str, Any]:
        """Estimate total page size including resources."""
        soup = BeautifulSoup(content, 'lxml')
        
        # Estimate sizes for different resource types
        resources = {
            'images': self._estimate_image_sizes(soup),
            'scripts': self._estimate_script_sizes(soup),
            'styles': self._estimate_style_sizes(soup)
        }
        
        total_size = sum(sum(sizes) for sizes in resources.values())
        html_size = len(content.encode('utf-8'))
        total_size += html_size
        
        return {
            'total_size_bytes': total_size,
            'resource_breakdown': resources,
            'total_size_acceptable': total_size <= self.size_thresholds['total']
        }
    
    def _estimate_image_sizes(self, soup: BeautifulSoup) -> list:
        """Estimate sizes of images on the page."""
        images = soup.find_all('img')
        # Rough estimation: assume average image size of 100KB
        return [100 * 1024 for _ in images]
    
    def _estimate_script_sizes(self, soup: BeautifulSoup) -> list:
        """Estimate sizes of scripts on the page."""
        scripts = soup.find_all('script', src=True)
        # Rough estimation: assume average script size of 50KB
        return [50 * 1024 for _ in scripts]
    
    def _estimate_style_sizes(self, soup: BeautifulSoup) -> list:
        """Estimate sizes of stylesheets on the page."""
        styles = soup.find_all('link', rel='stylesheet')
        # Rough estimation: assume average stylesheet size of 30KB
        return [30 * 1024 for _ in styles]
    
    def analyze(self, load_time: float, content: str) -> Dict[str, Any]:
        """Perform complete performance analysis."""
        return {
            'load_time': self.analyze_load_time(load_time),
            'page_size': self.analyze_page_size(content)
        } 