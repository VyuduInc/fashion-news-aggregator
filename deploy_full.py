import modal
import subprocess
import shlex

# Full container with all dependencies
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "streamlit==1.49.1",
    "feedparser==6.0.11",
    "requests==2.32.5", 
    "beautifulsoup4==4.13.5",
    "pandas==2.3.2",
    "python-dateutil==2.9.0.post0"
)

app = modal.App(name="fashion-news-aggregator", image=image)

@app.function(
    timeout=3600,
    memory=2048,
    cpu=2.0
)
@modal.concurrent(max_inputs=100)
@modal.web_server(8000)
def run():
    import os
    
    # Create directory structure
    os.makedirs("src", exist_ok=True)
    
    # Write database module
    with open("src/database.py", "w") as f:
        f.write('''import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

class ArticleDatabase:
    def __init__(self, db_path: str = "articles.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute(""\"
            CREATE TABLE IF NOT EXISTS articles (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                description TEXT,
                published_date DATETIME,
                source TEXT NOT NULL,
                category TEXT,
                content_hash TEXT UNIQUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ""\")
        conn.execute(""\"
            CREATE TABLE IF NOT EXISTS sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                url TEXT NOT NULL,
                rss_url TEXT,
                category TEXT,
                active INTEGER DEFAULT 1,
                last_updated DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ""\")
        conn.execute('CREATE INDEX IF NOT EXISTS idx_articles_published ON articles(published_date)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_articles_source ON articles(source)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_articles_category ON articles(category)')
        conn.commit()
        conn.close()
    
    def generate_article_id(self, title: str, url: str) -> str:
        content = f"{title}|{url}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def generate_content_hash(self, title: str, description: str) -> str:
        content = f"{title}|{description or ''}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def insert_article(self, article: Dict) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            article_id = self.generate_article_id(article['title'], article['url'])
            content_hash = self.generate_content_hash(article['title'], article.get('description', ''))
            
            conn.execute(""\"
                INSERT OR IGNORE INTO articles 
                (id, title, url, description, published_date, source, category, content_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ""\", (
                article_id, article['title'], article['url'], article.get('description'),
                article.get('published_date'), article['source'], article.get('category'), content_hash
            ))
            
            rows_affected = conn.total_changes
            conn.commit()
            conn.close()
            return rows_affected > 0
        except Exception as e:
            logging.error(f"Error inserting article: {e}")
            return False
    
    def get_articles(self, limit: int = 200, category: Optional[str] = None,
                    source: Optional[str] = None, hours_old: Optional[int] = None) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        query = "SELECT * FROM articles WHERE 1=1"
        params = []
        
        if category:
            query += " AND category = ?"
            params.append(category)
        if source:
            query += " AND source = ?"
            params.append(source)
        if hours_old is not None:
            cutoff_time = datetime.now() - timedelta(hours=hours_old)
            query += " AND published_date >= ?"
            params.append(cutoff_time.isoformat())
        
        query += " ORDER BY published_date DESC LIMIT ?"
        params.append(limit)
        
        cursor = conn.execute(query, params)
        articles = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return articles
    
    def cleanup_old_articles(self, days_old: int = 5):
        cutoff_date = datetime.now() - timedelta(days=days_old)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("DELETE FROM articles WHERE published_date < ?", (cutoff_date.isoformat(),))
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        logging.info(f"Cleaned up {deleted_count} old articles")
        return deleted_count
    
    def get_stats(self) -> Dict:
        conn = sqlite3.connect(self.db_path)
        total_articles = conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
        category_counts = dict(conn.execute(""\"
            SELECT category, COUNT(*) FROM articles WHERE category IS NOT NULL GROUP BY category
        ""\").fetchall())
        source_counts = dict(conn.execute(""\"
            SELECT source, COUNT(*) FROM articles GROUP BY source ORDER BY COUNT(*) DESC LIMIT 10
        ""\").fetchall())
        cutoff = datetime.now() - timedelta(hours=24)
        recent_count = conn.execute("SELECT COUNT(*) FROM articles WHERE published_date >= ?", (cutoff.isoformat(),)).fetchone()[0]
        conn.close()
        return {
            'total_articles': total_articles,
            'recent_articles_24h': recent_count,
            'by_category': category_counts,
            'top_sources': source_counts
        }
''')

    # Write feeds module
    with open("src/feeds.py", "w") as f:
        f.write('''FEED_SOURCES = {
    'Vogue': 'https://www.vogue.com/feed/rss',
    'WWD': 'https://wwd.com/feed/',
    'Business of Fashion': 'https://www.businessoffashion.com/feed/',
    'Harper\\'s Bazaar': 'https://www.harpersbazaar.com/rss/all.xml/',
    'Elle': 'https://www.elle.com/rss/all.xml/',
    'Marie Claire': 'https://www.marieclaire.com/rss/all.xml/',
    'Fashionista': 'https://fashionista.com/feed',
    'Glossy': 'https://glossy.co/feed/',
    'Allure': 'https://www.allure.com/feed/rss',
    'InStyle': 'https://www.instyle.com/syndication/rss',
    'Vogue UK': 'https://www.vogue.co.uk/rss',
    'Grazia': 'https://graziamagazine.com/feed/',
    'Stylist': 'https://www.stylist.co.uk/feed',
    'Refinery29': 'https://www.refinery29.com/rss.xml',
    'Who What Wear': 'https://www.whowhatwear.com/rss',
    'Hypebeast': 'https://hypebeast.com/feed',
    'Highsnobiety': 'https://www.highsnobiety.com/feed/',
    'Beauty Independent': 'https://www.beautyindependent.com/feed/',
    'Retail Dive': 'https://www.retaildive.com/feeds/news/',
    'Modern Retail': 'https://www.modernretail.co/feed/',
    'Byrdie': 'https://www.byrdie.com/rss',
    'Cosmopolitan': 'https://www.cosmopolitan.com/rss/all.xml/',
    'Teen Vogue': 'https://www.teenvogue.com/feed/rss',
    'The Cut': 'https://www.thecut.com/rss.xml'
}

def get_all_feeds():
    return FEED_SOURCES
''')

    # Write classifier module  
    with open("src/classifier.py", "w") as f:
        f.write('''import re
from typing import Dict, Optional

class ContentClassifier:
    def __init__(self):
        self.category_keywords = {
            'Fashion Business': ['revenue', 'sales', 'profit', 'earnings', 'CEO', 'investment', 'business', 'company'],
            'Beauty': ['makeup', 'cosmetics', 'skincare', 'beauty', 'lipstick', 'foundation', 'fragrance'],
            'Luxury': ['luxury', 'haute couture', 'high-end', 'premium', 'exclusive', 'Chanel', 'Louis Vuitton', 'Gucci'],
            'Retail': ['retail', 'store', 'shopping', 'mall', 'outlet', 'flagship', 'pop-up', 'brick-and-mortar'],
            'E-commerce': ['e-commerce', 'ecommerce', 'online shopping', 'digital', 'website', 'mobile app'],
            'Fashion Trends': ['trend', 'trending', 'fashion week', 'runway', 'collection', 'designer', 'style']
        }
        self.category_patterns = {}
        for category, keywords in self.category_keywords.items():
            pattern = r'\\\\b(?:' + '|'.join(re.escape(keyword) for keyword in keywords) + r')\\\\b'
            self.category_patterns[category] = re.compile(pattern, re.IGNORECASE)
    
    def classify_article(self, title: str, description: str = '') -> str:
        text = f"{title} {description or ''}"
        category_scores = {}
        for category, pattern in self.category_patterns.items():
            matches = pattern.findall(text)
            category_scores[category] = len(matches)
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            if category_scores[best_category] > 0:
                return best_category
        return 'Fashion Trends'
    
    def get_categories(self) -> list:
        return list(self.category_keywords.keys())
''')

    # Write aggregator module
    with open("src/aggregator.py", "w") as f:
        f.write('''import feedparser
import requests
from datetime import datetime, timezone
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
from src.database import ArticleDatabase
from src.classifier import ContentClassifier
from src.feeds import get_all_feeds

logging.basicConfig(level=logging.INFO)

class NewsAggregator:
    def __init__(self, db_path: str = "articles.db"):
        self.db = ArticleDatabase(db_path)
        self.classifier = ContentClassifier()
        self.feeds = get_all_feeds()
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Fashion News Aggregator 1.0'})
        
    def parse_feed_date(self, entry) -> datetime:
        try:
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                return datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
            else:
                return datetime.now(timezone.utc)
        except Exception:
            return datetime.now(timezone.utc)
    
    def fetch_single_feed(self, source_name: str, feed_url: str) -> List[Dict]:
        articles = []
        try:
            response = self.session.get(feed_url, timeout=30)
            response.raise_for_status()
            feed = feedparser.parse(response.content)
            
            for entry in feed.entries[:10]:  # Limit to 10 per feed for faster loading
                try:
                    title = entry.title if hasattr(entry, 'title') else 'No Title'
                    url = entry.link if hasattr(entry, 'link') else ''
                    description = entry.summary if hasattr(entry, 'summary') else ''
                    
                    if not url:
                        continue
                    
                    published_date = self.parse_feed_date(entry)
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
            logging.info(f"Fetched {len(articles)} articles from {source_name}")
        except Exception as e:
            logging.error(f"Error fetching {source_name}: {e}")
        return articles
    
    def fetch_all_feeds(self, max_workers: int = 5) -> int:  # Reduced workers for better stability
        total_new_articles = 0
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_source = {
                executor.submit(self.fetch_single_feed, source, url): source 
                for source, url in list(self.feeds.items())[:20]  # Start with 20 sources
            }
            
            for future in as_completed(future_to_source):
                source_name = future_to_source[future]
                try:
                    articles = future.result()
                    new_count = 0
                    for article in articles:
                        if self.db.insert_article(article):
                            new_count += 1
                    total_new_articles += new_count
                    logging.info(f"Added {new_count} new articles from {source_name}")
                except Exception as e:
                    logging.error(f"Error processing results from {source_name}: {e}")
        
        deleted_count = self.db.cleanup_old_articles(days_old=5)
        logging.info(f"Total new articles added: {total_new_articles}")
        return total_new_articles
    
    def get_recent_articles(self, limit: int = 200, category: str = None, source: str = None, hours_old: int = None) -> List[Dict]:
        return self.db.get_articles(limit=limit, category=category, source=source, hours_old=hours_old)
    
    def get_stats(self) -> Dict:
        return self.db.get_stats()
    
    def get_sources(self) -> List[str]:
        return list(self.feeds.keys())
    
    def get_categories(self) -> List[str]:
        return self.classifier.get_categories()
''')

    # Write __init__.py
    with open("src/__init__.py", "w") as f:
        f.write("# Fashion & Beauty News Aggregator")

    # Write main Streamlit app
    with open("app.py", "w") as f:
        f.write('''import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
sys.path.append('.')

try:
    from src.aggregator import NewsAggregator
    AGGREGATOR_AVAILABLE = True
except ImportError:
    AGGREGATOR_AVAILABLE = False

st.set_page_config(
    page_title="Fashion & Beauty News Aggregator",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional dark theme
st.markdown("""
<style>
    .main > div { padding-top: 2rem; }
    .stTitle { color: #FFFFFF; font-size: 2.5rem; font-weight: 700; margin-bottom: 1rem; text-align: center; }
    .article-card { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 1rem; margin-bottom: 0.5rem; }
    .article-title { color: #FFFFFF; font-size: 1.1rem; font-weight: 600; margin-bottom: 0.5rem; }
    .article-meta { color: #A0A0A0; font-size: 0.9rem; margin-bottom: 0.5rem; }
    .article-source { color: #4CAF50; font-weight: 500; }
    .article-category { background: rgba(76, 175, 80, 0.2); color: #4CAF50; padding: 0.2rem 0.5rem; border-radius: 15px; font-size: 0.8rem; }
    .article-description { color: #CCCCCC; font-size: 0.9rem; line-height: 1.5; margin-bottom: 0.5rem; }
    .read-more-btn { background: #4CAF50; color: white; padding: 0.4rem 1rem; border: none; border-radius: 5px; text-decoration: none; font-size: 0.9rem; display: inline-block; }
</style>
""", unsafe_allow_html=True)

def format_time_ago(published_date):
    if not published_date:
        return "Unknown time"
    try:
        if isinstance(published_date, str):
            pub_date = datetime.fromisoformat(published_date.replace('Z', '+00:00'))
        else:
            pub_date = published_date
        now = datetime.now(pub_date.tzinfo) if pub_date.tzinfo else datetime.now()
        diff = now - pub_date
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"
    except:
        return "Unknown time"

@st.cache_data(ttl=1800)
def load_aggregator():
    if not AGGREGATOR_AVAILABLE:
        return None
    try:
        return NewsAggregator()
    except Exception as e:
        st.error(f"Error loading aggregator: {e}")
        return None

def main():
    st.markdown('<h1 class="stTitle">👗 Fashion & Beauty News Aggregator</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #A0A0A0; margin-bottom: 2rem;">Latest news from 20+ international fashion, beauty, luxury, and retail sources</p>', unsafe_allow_html=True)
    
    # Load aggregator
    aggregator = load_aggregator()
    
    if not aggregator:
        st.error("📊 Loading news aggregator...")
        st.info("🔄 Initializing database and fetching articles...")
        
        # Try to initialize
        try:
            if AGGREGATOR_AVAILABLE:
                aggregator = NewsAggregator()
                with st.spinner("Fetching latest articles..."):
                    new_articles = aggregator.fetch_all_feeds()
                st.success(f"✅ Loaded {new_articles} articles!")
                st.rerun()
        except Exception as e:
            st.error(f"Error initializing: {e}")
        return
    
    # Sidebar filters
    with st.sidebar:
        st.header("🔍 Filters")
        
        # Time filter
        time_options = ["All time", "1 hour", "12 hours", "1 day", "2 days", "3 days"]
        time_filter = st.selectbox("📅 Time Range", time_options, index=0)
        
        # Get data for filters
        try:
            categories = aggregator.get_categories()
            sources = aggregator.get_sources()
            stats = aggregator.get_stats()
            
            # Category filter
            category_options = ["All Categories"] + categories
            category_filter = st.selectbox("🏷️ Category", category_options, index=0)
            
            # Source filter  
            source_options = ["All Sources"] + sorted(sources)
            source_filter = st.selectbox("📰 Source", source_options, index=0)
            
            # Article limit
            article_limit = st.slider("📊 Articles to Show", 50, 200, 100, 25)
            
            # Show stats
            st.markdown("### 📈 Statistics")
            st.metric("Total Articles", stats.get('total_articles', 0))
            st.metric("Last 24 Hours", stats.get('recent_articles_24h', 0))
            
        except Exception as e:
            st.error(f"Error loading filters: {e}")
            return
    
    # Main content
    col1, col2 = st.columns([3, 1])
    
    with col2:
        if st.button("🔄 Refresh Articles", type="primary"):
            st.cache_data.clear()
            try:
                new_articles = aggregator.fetch_all_feeds()
                st.success(f"✅ Added {new_articles} new articles!")
            except Exception as e:
                st.error(f"Error refreshing: {e}")
            st.rerun()
    
    with col1:
        st.markdown(f"### Latest Articles ({time_filter})")
    
    # Load articles
    try:
        hours_old = None
        if time_filter == "1 hour": hours_old = 1
        elif time_filter == "12 hours": hours_old = 12
        elif time_filter == "1 day": hours_old = 24
        elif time_filter == "2 days": hours_old = 48
        elif time_filter == "3 days": hours_old = 72
        
        articles = aggregator.get_recent_articles(
            limit=article_limit,
            category=category_filter if category_filter != "All Categories" else None,
            source=source_filter if source_filter != "All Sources" else None,
            hours_old=hours_old
        )
        
        if not articles:
            st.warning("No articles found. Try refreshing or adjusting filters.")
            return
        
        # Display articles
        for article in articles:
            st.markdown('<div class="article-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="article-title">{article["title"]}</div>', unsafe_allow_html=True)
            
            time_ago = format_time_ago(article.get('published_date'))
            st.markdown(
                f'<div class="article-meta">'
                f'<span class="article-source">{article["source"]}</span> • {time_ago} • '
                f'<span class="article-category">{article.get("category", "Uncategorized")}</span>'
                f'</div>',
                unsafe_allow_html=True
            )
            
            if article.get('description'):
                description = article['description'][:200] + "..." if len(article['description']) > 200 else article['description']
                st.markdown(f'<div class="article-description">{description}</div>', unsafe_allow_html=True)
            
            st.markdown(f'<a href="{article["url"]}" target="_blank" class="read-more-btn">Read Full Article →</a>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        # Stats
        st.markdown(f"---")
        st.markdown(f"**Showing {len(articles)} articles**")
        
        if stats.get('by_category'):
            st.markdown("### 📊 Articles by Category")
            category_df = pd.DataFrame([
                {"Category": cat, "Count": count} 
                for cat, count in stats['by_category'].items()
            ])
            st.bar_chart(category_df.set_index('Category'))
            
    except Exception as e:
        st.error(f"Error loading articles: {e}")

if __name__ == "__main__":
    main()
''')
    
    print("🚀 Starting news aggregation...")
    
    # Run initial aggregation in background
    import subprocess
    subprocess.Popen([
        "python", "-c", 
        "import sys; sys.path.append('.'); "
        "from src.aggregator import NewsAggregator; "
        "agg = NewsAggregator(); "
        "new = agg.fetch_all_feeds(); "
        "print(f'Initial load: {new} articles')"
    ])
    
    # Start Streamlit
    subprocess.run([
        "streamlit", "run", "app.py",
        "--server.port", "8000",
        "--server.enableCORS", "false",
        "--server.enableXsrfProtection", "false", 
        "--server.headless", "true"
    ])

if __name__ == "__main__":
    app.serve()