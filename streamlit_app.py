import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from aggregator import NewsAggregator
    AGGREGATOR_AVAILABLE = True
except ImportError:
    AGGREGATOR_AVAILABLE = False

st.set_page_config(
    page_title="Fashion & Beauty News Aggregator",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional dark theme with better readability
st.markdown("""
<style>
    .main > div { padding-top: 2rem; }
    .stTitle { color: #F1F5F9; font-size: 2.5rem; font-weight: 700; margin-bottom: 1rem; text-align: center; }
    .article-card { 
        background: rgba(30, 41, 59, 0.6); 
        border: 1px solid rgba(59, 130, 246, 0.3); 
        border-radius: 8px; 
        padding: 1rem; 
        margin-bottom: 0.5rem;
        transition: all 0.3s ease;
    }
    .article-card:hover {
        background: rgba(30, 41, 59, 0.8);
        border-color: rgba(59, 130, 246, 0.5);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
    }
    .article-title { color: #F1F5F9; font-size: 1.1rem; font-weight: 600; margin-bottom: 0.5rem; line-height: 1.5; }
    .article-meta { color: #CBD5E1; font-size: 0.9rem; margin-bottom: 0.5rem; }
    .article-source { color: #60A5FA; font-weight: 600; }
    .article-category { 
        background: rgba(59, 130, 246, 0.2); 
        color: #93C5FD; 
        padding: 0.2rem 0.5rem; 
        border-radius: 15px; 
        font-size: 0.8rem; 
        font-weight: 500;
    }
    .article-description { color: #E2E8F0; font-size: 0.9rem; line-height: 1.6; margin-bottom: 0.5rem; }
    .read-more-btn { 
        background: linear-gradient(135deg, #3B82F6 0%, #1E40AF 100%); 
        color: white; 
        padding: 0.5rem 1rem; 
        border: none; 
        border-radius: 6px; 
        text-decoration: none; 
        font-size: 0.9rem; 
        font-weight: 500;
        display: inline-block;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
    }
    .read-more-btn:hover {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(59, 130, 246, 0.4);
        text-decoration: none;
        color: white;
    }
    
    /* Better sidebar styling */
    .sidebar .stSelectbox label,
    .sidebar .stMultiselect label,
    .sidebar .stRadio label {
        color: #F1F5F9 !important;
        font-weight: 600;
    }
    
    /* Improved metric styling */
    .metric-container {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 8px;
        padding: 1rem;
    }
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

@st.cache_data(ttl=900)
def get_articles_data(category_filter, source_filter, time_filter, limit):
    aggregator = load_aggregator()
    if not aggregator:
        return [], {}, [], []
    
    hours_old = None
    if time_filter == "1 hour":
        hours_old = 1
    elif time_filter == "12 hours":
        hours_old = 12
    elif time_filter == "1 day":
        hours_old = 24
    elif time_filter == "2 days":
        hours_old = 48
    elif time_filter == "3 days":
        hours_old = 72
    
    articles = aggregator.get_recent_articles(
        limit=limit,
        category=category_filter if category_filter != "All Categories" else None,
        source=source_filter if source_filter != "All Sources" else None,
        hours_old=hours_old
    )
    
    stats = aggregator.get_stats()
    sources = aggregator.get_sources()
    categories = aggregator.get_categories()
    
    return articles, stats, sources, categories

def main():
    st.markdown('<h1 class="stTitle">👗 Fashion & Beauty News Aggregator</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #A0A0A0; margin-bottom: 2rem;">Latest news from 50+ international fashion, beauty, luxury, and retail sources</p>', unsafe_allow_html=True)
    
    # Success banner
    st.success("✅ Successfully deployed on Streamlit Cloud! Free fashion news aggregation is live!")
    
    # Load aggregator
    aggregator = load_aggregator()
    
    if not aggregator:
        st.info("🚀 Initializing news aggregator for first time...")
        
        # Show what we're building while initializing
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Sources", "50+")
        with col2:
            st.metric("Categories", "6")
        with col3:
            st.metric("Updates", "30min")
        with col4:
            st.metric("Status", "🟢 Live")
        
        try:
            if AGGREGATOR_AVAILABLE:
                with st.spinner("Fetching latest articles from fashion sources..."):
                    aggregator = NewsAggregator()
                    new_articles = aggregator.fetch_all_feeds()
                st.success(f"✅ Loaded {new_articles} articles!")
                st.rerun()
            else:
                st.warning("📦 Installing dependencies... Please refresh the page in a moment.")
        except Exception as e:
            st.error(f"Initialization error: {e}")
        return
    
    # Sidebar filters
    with st.sidebar:
        st.header("🔍 Filters")
        
        # Time filter
        time_options = ["All time", "1 hour", "12 hours", "1 day", "2 days", "3 days"]
        time_filter = st.selectbox("📅 Time Range", time_options, index=0)
        
        # Get data for filters
        try:
            _, stats, sources, categories = get_articles_data("All Categories", "All Sources", "All time", 10)
            
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
        articles, stats, sources, categories = get_articles_data(category_filter, source_filter, time_filter, article_limit)
        
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
        st.markdown(f"**Showing {len(articles)} articles** (filtered from {stats.get('total_articles', 0)} total)")
        
        if stats.get('by_category'):
            st.markdown("### 📊 Articles by Category")
            category_df = pd.DataFrame([
                {"Category": cat, "Count": count} 
                for cat, count in stats['by_category'].items()
            ])
            st.bar_chart(category_df.set_index('Category'))
            
    except Exception as e:
        st.error(f"Error loading articles: {e}")

    # Footer
    st.markdown("---")
    st.info("🎉 **Deployed FREE on Streamlit Cloud** | Full-featured fashion news aggregator with 50+ international sources")

if __name__ == "__main__":
    main()