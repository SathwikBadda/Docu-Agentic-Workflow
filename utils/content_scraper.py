import requests
from bs4 import BeautifulSoup
import html2text
from playwright.sync_api import sync_playwright
import re

class ContentScraper:
    def __init__(self):
        self.h = html2text.HTML2Text()
        self.h.ignore_links = False
        self.h.ignore_images = False
        
    def scrape_url(self, url: str) -> dict:
        """Scrape content from URL using both requests and playwright as fallback"""
        try:
            # Try requests first (faster)
            content = self._scrape_with_requests(url)
            if content and len(content.get('text', '')) > 100:
                return content
        except Exception as e:
            print(f"Requests failed: {e}")
        
        try:
            # Fallback to playwright for dynamic content
            return self._scrape_with_playwright(url)
        except Exception as e:
            print(f"Playwright failed: {e}")
            return {"error": f"Failed to scrape content: {e}"}
    
    def _scrape_with_requests(self, url: str) -> dict:
        """Scrape using requests and BeautifulSoup"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        return self._extract_content(soup, url)
    
    def _scrape_with_playwright(self, url: str) -> dict:
        """Scrape using playwright for dynamic content"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until='networkidle')
            
            html_content = page.content()
            browser.close()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            return self._extract_content(soup, url)
    
    def _extract_content(self, soup: BeautifulSoup, url: str) -> dict:
        """Extract and clean content from BeautifulSoup object"""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get title
        title = soup.find('title')
        title_text = title.get_text().strip() if title else "Untitled"
        
        # Find main content area
        main_content = self._find_main_content(soup)
        
        # Convert to markdown
        html_content = str(main_content)
        markdown_text = self.h.handle(html_content)
        
        # Clean up markdown
        cleaned_text = self._clean_markdown(markdown_text)
        
        return {
            "title": title_text,
            "url": url,
            "html": html_content,
            "markdown": markdown_text,
            "text": cleaned_text,
            "word_count": len(cleaned_text.split()),
            "headings": self._extract_headings(main_content)
        }
    
    def _find_main_content(self, soup: BeautifulSoup):
        """Find the main content area of the page"""
        # Try common content containers
        selectors = [
            'main', 'article', '[role="main"]',
            '.content', '.main-content', '.article-content',
            '.documentation', '.docs-content', '.doc-content'
        ]
        
        for selector in selectors:
            content = soup.select_one(selector)
            if content:
                return content
        
        # Fallback to body
        return soup.find('body') or soup
    
    def _extract_headings(self, content):
        """Extract headings structure"""
        headings = []
        for heading in content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            headings.append({
                'level': int(heading.name[1]),
                'text': heading.get_text().strip()
            })
        return headings
    
    def _clean_markdown(self, markdown_text: str) -> str:
        """Clean and normalize markdown text"""
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', markdown_text)
        
        # Remove markdown links but keep text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        
        # Clean up common artifacts
        text = re.sub(r'\*\*\s*\*\*', '', text)
        text = re.sub(r'__\s*__', '', text)
        
        return text.strip()