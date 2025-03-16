#!/usr/bin/env python3

import argparse
import json
import logging
from urllib.parse import urljoin, urlparse
from typing import Set, Dict, List, Any
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from tqdm import tqdm
import validators
from concurrent.futures import ThreadPoolExecutor
import time

from utils.robots_parser import RobotsParser
from analyzers.seo_analyzer import SEOAnalyzer
from analyzers.performance_analyzer import PerformanceAnalyzer
from analyzers.content_analyzer import ContentAnalyzer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SEOCrawler:
    def __init__(self, base_url: str, depth: int = 3, timeout: int = 30, ignore_robots: bool = False):
        self.base_url = base_url
        self.depth = depth
        self.timeout = timeout
        self.ignore_robots = ignore_robots
        self.visited_urls: Set[str] = set()
        self.results: Dict[str, Any] = {}
        self.user_agent = UserAgent()
        
        # Initialize analyzers
        self.seo_analyzer = SEOAnalyzer()
        self.performance_analyzer = PerformanceAnalyzer()
        self.content_analyzer = ContentAnalyzer()
        
        # Setup robots.txt parser
        self.robots_parser = RobotsParser(base_url)
        
    def is_valid_url(self, url: str) -> bool:
        """Validate if the URL is valid and belongs to the same domain."""
        if not validators.url(url):
            return False
        return urlparse(url).netloc == urlparse(self.base_url).netloc
    
    def get_page_content(self, url: str) -> tuple[str, float]:
        """Fetch page content and measure load time."""
        headers = {'User-Agent': self.user_agent.random}
        start_time = time.time()
        response = requests.get(url, headers=headers, timeout=self.timeout)
        load_time = time.time() - start_time
        return response.text, load_time
    
    def extract_links(self, soup: BeautifulSoup, current_url: str) -> List[str]:
        """Extract all valid links from the page."""
        links = []
        for anchor in soup.find_all('a', href=True):
            href = anchor['href']
            absolute_url = urljoin(current_url, href)
            if self.is_valid_url(absolute_url):
                links.append(absolute_url)
        return links
    
    def analyze_page(self, url: str, depth: int) -> Dict[str, Any]:
        """Analyze a single page for SEO metrics."""
        if depth > self.depth or url in self.visited_urls:
            return {}
        
        if not self.ignore_robots and not self.robots_parser.can_fetch(url):
            logger.info(f"Skipping {url} as per robots.txt rules")
            return {}
        
        self.visited_urls.add(url)
        
        try:
            content, load_time = self.get_page_content(url)
            soup = BeautifulSoup(content, 'lxml')
            
            # Collect all analysis results
            seo_metrics = self.seo_analyzer.analyze(soup, url)
            performance_metrics = self.performance_analyzer.analyze(load_time, content)
            content_metrics = self.content_analyzer.analyze(soup)
            
            # Extract and crawl links
            links = self.extract_links(soup, url)
            
            result = {
                'url': url,
                'depth': depth,
                'seo_metrics': seo_metrics,
                'performance_metrics': performance_metrics,
                'content_metrics': content_metrics,
                'links': links
            }
            
            # Recursively crawl linked pages
            with ThreadPoolExecutor(max_workers=5) as executor:
                future_to_url = {
                    executor.submit(self.analyze_page, link, depth + 1): link
                    for link in links if link not in self.visited_urls
                }
                
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing {url}: {str(e)}")
            return {'url': url, 'error': str(e)}
    
    def crawl(self) -> Dict[str, Any]:
        """Start the crawling process and return results."""
        logger.info(f"Starting crawl of {self.base_url}")
        self.results = self.analyze_page(self.base_url, 0)
        return self.results
    
    def save_report(self, output_file: str):
        """Save the analysis results to a JSON file."""
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        logger.info(f"Report saved to {output_file}")

def main():
    parser = argparse.ArgumentParser(description='SEO Site Crawler')
    parser.add_argument('--url', required=True, help='Target website URL')
    parser.add_argument('--depth', type=int, default=3, help='Maximum crawling depth')
    parser.add_argument('--output', default='seo_report.json', help='Output file path')
    parser.add_argument('--timeout', type=int, default=30, help='Request timeout in seconds')
    parser.add_argument('--ignore-robots', action='store_true', help='Ignore robots.txt rules')
    
    args = parser.parse_args()
    
    crawler = SEOCrawler(
        base_url=args.url,
        depth=args.depth,
        timeout=args.timeout,
        ignore_robots=args.ignore_robots
    )
    
    results = crawler.crawl()
    crawler.save_report(args.output)

if __name__ == '__main__':
    main() 