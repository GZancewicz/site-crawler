import urllib.robotparser
from urllib.parse import urljoin
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class RobotsParser:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.parser = urllib.robotparser.RobotFileParser()
        self.initialize_parser()
    
    def initialize_parser(self):
        """Initialize the robots.txt parser."""
        try:
            robots_url = urljoin(self.base_url, '/robots.txt')
            self.parser.set_url(robots_url)
            self.parser.read()
        except Exception as e:
            logger.warning(f"Could not fetch robots.txt: {str(e)}")
            # If we can't fetch robots.txt, assume everything is allowed
            self.parser = None
    
    def can_fetch(self, url: str, user_agent: str = '*') -> bool:
        """Check if the URL can be fetched according to robots.txt rules."""
        if self.parser is None:
            return True
        try:
            return self.parser.can_fetch(user_agent, url)
        except Exception as e:
            logger.warning(f"Error checking robots.txt rules: {str(e)}")
            return True  # In case of error, we'll be permissive
    
    def get_crawl_delay(self, user_agent: str = '*') -> Optional[float]:
        """Get the crawl delay specified in robots.txt."""
        if self.parser is None:
            return None
        try:
            return self.parser.crawl_delay(user_agent)
        except Exception:
            return None 