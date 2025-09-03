import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

class ArticleDatabase:
    def __init__(self, db_path: str = "articles.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
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
        ''')
        
        conn.execute('''
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
        ''')
        
        # Create indexes for better query performance
        conn.execute('CREATE INDEX IF NOT EXISTS idx_articles_published ON articles(published_date)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_articles_source ON articles(source)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_articles_category ON articles(category)')
        
        conn.commit()
        conn.close()
    
    def generate_article_id(self, title: str, url: str) -> str:
        """Generate unique ID for article based on title and URL"""
        content = f"{title}|{url}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def generate_content_hash(self, title: str, description: str) -> str:
        """Generate hash for content deduplication"""
        content = f"{title}|{description or ''}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def insert_article(self, article: Dict) -> bool:
        """Insert new article, return True if successful"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Generate IDs and hashes
            article_id = self.generate_article_id(article['title'], article['url'])
            content_hash = self.generate_content_hash(article['title'], article.get('description', ''))
            
            conn.execute('''
                INSERT OR IGNORE INTO articles 
                (id, title, url, description, published_date, source, category, content_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                article_id,
                article['title'],
                article['url'],
                article.get('description'),
                article.get('published_date'),
                article['source'],
                article.get('category'),
                content_hash
            ))
            
            rows_affected = conn.total_changes
            conn.commit()
            conn.close()
            
            return rows_affected > 0
            
        except sqlite3.IntegrityError:
            # Article already exists
            return False
        except Exception as e:
            logging.error(f"Error inserting article: {e}")
            return False
    
    def get_articles(self, 
                    limit: int = 200,
                    category: Optional[str] = None,
                    source: Optional[str] = None,
                    hours_old: Optional[int] = None) -> List[Dict]:
        """Get articles with optional filtering"""
        
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
        """Remove articles older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "DELETE FROM articles WHERE published_date < ?",
            (cutoff_date.isoformat(),)
        )
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        logging.info(f"Cleaned up {deleted_count} old articles")
        return deleted_count
    
    def get_sources(self) -> List[Dict]:
        """Get all sources"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        cursor = conn.execute("SELECT * FROM sources WHERE active = 1")
        sources = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return sources
    
    def insert_source(self, name: str, url: str, rss_url: str, category: str = None):
        """Insert new source"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute('''
                INSERT OR IGNORE INTO sources (name, url, rss_url, category)
                VALUES (?, ?, ?, ?)
            ''', (name, url, rss_url, category))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error inserting source: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        
        # Total articles
        total_articles = conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
        
        # Articles by category
        category_counts = dict(conn.execute('''
            SELECT category, COUNT(*) 
            FROM articles 
            WHERE category IS NOT NULL 
            GROUP BY category
        ''').fetchall())
        
        # Articles by source
        source_counts = dict(conn.execute('''
            SELECT source, COUNT(*) 
            FROM articles 
            GROUP BY source 
            ORDER BY COUNT(*) DESC 
            LIMIT 10
        ''').fetchall())
        
        # Recent articles (last 24h)
        cutoff = datetime.now() - timedelta(hours=24)
        recent_count = conn.execute(
            "SELECT COUNT(*) FROM articles WHERE published_date >= ?",
            (cutoff.isoformat(),)
        ).fetchone()[0]
        
        conn.close()
        
        return {
            'total_articles': total_articles,
            'recent_articles_24h': recent_count,
            'by_category': category_counts,
            'top_sources': source_counts
        }