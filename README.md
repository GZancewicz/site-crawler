# SEO Site Crawler

A comprehensive website crawler and SEO analysis tool that helps evaluate websites for search engine optimization factors.

## Features

- Website crawling with robots.txt compliance
- Analysis of meta tags and SEO elements
- Header structure evaluation
- Image alt text checking
- URL structure analysis
- Page load speed measurement
- Mobile responsiveness checking
- Internal and external link analysis
- Content quality metrics
- Detailed SEO reports generation

## Installation

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

```bash
python seo_crawler.py --url https://example.com --depth 3 --output report.json
```

### Arguments

- `--url`: The target website URL to crawl
- `--depth`: Maximum crawling depth (default: 3)
- `--output`: Output file path for the SEO report (default: seo_report.json)
- `--ignore-robots`: Ignore robots.txt rules (not recommended)
- `--timeout`: Request timeout in seconds (default: 30)

## Output

The tool generates a comprehensive SEO report including:
- Overall SEO score
- Detailed analysis of each page
- Specific recommendations for improvement
- Technical issues found
- Content optimization suggestions

## License

MIT License