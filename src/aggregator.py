import feedparser
import requests
from datetime import datetime, timezone
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
from src.database import ArticleDatabase
from src.classifier import ContentClassifier
from src.feeds import get_all_feeds
import traceback

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class NewsAggregator:
    def __init__(self, db_path: str = "articles.db"):
        self.db = ArticleDatabase(db_path)
        self.classifier = ContentClassifier()
        self.feeds = get_all_feeds()
        
        # Request session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Fashion News Aggregator 1.0 (Educational Use)'
        })
        
    def parse_feed_date(self, entry) -> datetime:
        """Parse feed entry date to datetime object"""
        try:
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                return datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
            else:
                # Fallback to current time if no date found
                return datetime.now(timezone.utc)
        except Exception:
            return datetime.now(timezone.utc)
    
    def fetch_single_feed(self, source_name: str, feed_url: str) -> List[Dict]:
        """Fetch and parse a single RSS feed"""
        articles = []
        
        try:
            # Set timeout for feed parsing
            response = self.session.get(feed_url, timeout=30)
            response.raise_for_status()
            
            # Parse RSS feed
            feed = feedparser.parse(response.content)
            
            if feed.bozo and hasattr(feed, 'bozo_exception'):
                logging.warning(f"Feed parsing warning for {source_name}: {feed.bozo_exception}")
            
            for entry in feed.entries[:20]:  # Limit to 20 most recent articles per feed
                try:
                    title = entry.title if hasattr(entry, 'title') else 'No Title'
                    url = entry.link if hasattr(entry, 'link') else ''
                    description = entry.summary if hasattr(entry, 'summary') else ''
                    
                    if not url:
                        continue
                    
                    # Parse publication date
                    published_date = self.parse_feed_date(entry)
                    
                    # Classify article
                    category = self.classifier.classify_article(title, description)
                    
                    article = {
                        'title': title.strip(),
                        'url': url.strip(),
                        'description': description.strip() if description else None,
                        'published_date': published_date,
                        'source': source_name,
                        'category': category
                    }
                    
                    articles.append(article)
                    
                except Exception as e:
                    logging.error(f"Error processing entry from {source_name}: {e}")
                    continue
                    
            logging.info(f"Successfully fetched {len(articles)} articles from {source_name}")
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Network error fetching {source_name}: {e}")
        except Exception as e:
            logging.error(f"Unexpected error fetching {source_name}: {e}")
            logging.error(traceback.format_exc())
        
        return articles
    
    def fetch_all_feeds(self, max_workers: int = 10) -> int:
        """Fetch all RSS feeds concurrently"""
        total_new_articles = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all feed fetch tasks
            future_to_source = {
                executor.submit(self.fetch_single_feed, source, url): source 
                for source, url in self.feeds.items()
            }
            
            # Process completed tasks
            for future in as_completed(future_to_source):
                source_name = future_to_source[future]
                
                try:
                    articles = future.result()
                    
                    # Insert articles into database
                    new_count = 0
                    for article in articles:
                        if self.db.insert_article(article):
                            new_count += 1
                    
                    total_new_articles += new_count
                    logging.info(f"Added {new_count} new articles from {source_name}")
                    
                except Exception as e:
                    logging.error(f"Error processing results from {source_name}: {e}")
        
        # Clean up old articles
        deleted_count = self.db.cleanup_old_articles(days_old=5)
        logging.info(f"Cleaned up {deleted_count} old articles")
        
        logging.info(f"Total new articles added: {total_new_articles}")
        return total_new_articles
    
    def get_recent_articles(self, 
                          limit: int = 200,
                          category: str = None,
                          source: str = None,
                          hours_old: float = None) -> List[Dict]:
        """Get recent articles with filtering"""
        return self.db.get_articles(
            limit=limit,
            category=category,
            source=source,
            hours_old=hours_old
        )
    
    def get_stats(self) -> Dict:
        """Get aggregator statistics"""
        return self.db.get_stats()
    
    def get_sources(self) -> List[str]:
        """Get list of all sources"""
        return list(self.feeds.keys())
    
    def get_categories(self) -> List[str]:
        """Get list of all categories"""
        return self.classifier.get_categories()

def main():
    """Main function for testing"""
    aggregator = NewsAggregator()
    
    print("Starting news aggregation...")
    new_articles = aggregator.fetch_all_feeds()
    
    print(f"\nAggregation complete. {new_articles} new articles added.")
    
    # Show stats
    stats = aggregator.get_stats()
    print(f"\nDatabase Statistics:")
    print(f"Total articles: {stats['total_articles']}")
    print(f"Articles in last 24h: {stats['recent_articles_24h']}")
    print(f"\nTop sources:")
    for source, count in list(stats['top_sources'].items())[:10]:
        print(f"  {source}: {count}")
    print(f"\nBy category:")
    for category, count in stats['by_category'].items():
        print(f"  {category}: {count}")

if __name__ == "__main__":
    main()