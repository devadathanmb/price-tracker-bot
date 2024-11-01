from typing import Dict, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor
from config import Config
from utils.logger import get_logger
from .prompt import SCRAPE_PROMPT
from scrapegraphai.graphs import SmartScraperGraph

logger = get_logger(__name__)

class SmartScraper:
    """
    Scraper class that uses AI to extract product information from web pages.
    """
    
    def __init__(self):
        self.graph_config = {
            "llm": {
                "model": Config.LLM_MODEL,
                "api_key": Config.LLM_TOKEN,
                "temperature": Config.LLM_TEMPERATURE,
            }
        }
        self.executor = ThreadPoolExecutor()

    async def scrape(self, *, url: str) -> Dict[str, Optional[str]]:
        """
        Asynchronously scrape product information from a URL.
        
        Args:
            url: The URL to scrape
            
        Returns:
            Dictionary containing product information
        """
        try:
            logger.info(f"Starting scrape for URL: {url}")
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(self.executor, self._scrape, url)
            logger.info(f"Scrape completed for URL: {url}")
            return result
        except Exception as e:
            logger.error(f"Error scraping URL {url}: {str(e)}")
            return {
                "is_trackable": False,
                "product_name": None,
                "price": None,
                "currency": None
            }

    def _scrape(self, url: str) -> Dict[str, Optional[str]]:
        """
        Perform the actual scraping operation.
        
        Args:
            url: The URL to scrape
            
        Returns:
            Dictionary containing product information
        """
        try:
            smart_scraper_graph = SmartScraperGraph(
                prompt=SCRAPE_PROMPT,
                source=url,
                config=self.graph_config,
            )
            return smart_scraper_graph.run()
        except Exception as e:
            logger.error(f"Error in _scrape: {str(e)}")
            raise

# Create a single instance for use throughout the application
scraper = SmartScraper()

if __name__ == "__main__":
    # Example usage
    test_url = "https://www.flipkart.com/product-example"
    result = asyncio.run(scraper.scrape(url=test_url))
    print(result)
