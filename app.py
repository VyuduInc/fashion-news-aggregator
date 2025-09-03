import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from src.aggregator import NewsAggregator
from src.classifier import ContentClassifier
import time

# Page config
st.set_page_config(
    page_title="Fashion & Beauty News Aggregator",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme and professional styling
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    
    .stTitle {
        color: #FFFFFF;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .metric-container {
        background: rgba(255, 255, 255, 0.05);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .article-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.5rem;
        transition: all 0.3s ease;
    }
    
    .article-card:hover {
        background: rgba(255, 255, 255, 0.08);
        border-color: rgba(255, 255, 255, 0.3);
    }
    
    .article-title {
        color: #FFFFFF;
        font-size: 1.1rem;
        font-weight: 600;
        line-height: 1.4;
        margin-bottom: 0.5rem;
    }
    
    .article-meta {
        color: #A0A0A0;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }
    
    .article-source {
        color: #4CAF50;
        font-weight: 500;
    }
    
    .article-category {
        background: rgba(76, 175, 80, 0.2);
        color: #4CAF50;
        padding: 0.2rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
        margin-right: 0.5rem;
    }
    
    .article-description {
        color: #CCCCCC;
        font-size: 0.9rem;
        line-height: 1.5;
        margin-bottom: 0.5rem;
    }
    
    .read-more-btn {
        background: #4CAF50;
        color: white;
        padding: 0.4rem 1rem;
        border: none;
        border-radius: 5px;
        text-decoration: none;
        font-size: 0.9rem;
        font-weight: 500;
        display: inline-block;
        transition: background 0.3s ease;
    }
    
    .read-more-btn:hover {
        background: #45a049;
        text-decoration: none;
        color: white;
    }
    
    .sidebar .stSelectbox label,
    .sidebar .stMultiselect label,
    .sidebar .stRadio label {
        color: #FFFFFF !important;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def load_aggregator():
    """Load and cache the news aggregator"""
    return NewsAggregator()

@st.cache_data(ttl=900)  # Cache for 15 minutes
def get_articles_data(category_filter, source_filter, time_filter, limit):
    """Get articles data with caching"""
    aggregator = load_aggregator()
    
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
    
    return articles, aggregator.get_stats(), aggregator.get_sources(), aggregator.get_categories()

def format_time_ago(published_date):
    """Format time ago string"""
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

def main():
    # Header
    st.markdown('<h1 class="stTitle">👗 Fashion & Beauty News Aggregator</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #A0A0A0; margin-bottom: 2rem;">Latest news from 50+ international fashion, beauty, luxury, and retail sources</p>', unsafe_allow_html=True)
    
    # Sidebar filters
    with st.sidebar:
        st.header("🔍 Filters")
        
        # Auto-refresh toggle
        auto_refresh = st.checkbox("Auto-refresh (30s)", value=False)
        
        # Time filter
        time_options = ["All time", "1 hour", "12 hours", "1 day", "2 days", "3 days"]
        time_filter = st.selectbox("📅 Time Range", time_options, index=0)
        
        # Load data to get available categories and sources
        try:
            sample_articles, stats, sources, categories = get_articles_data("All Categories", "All Sources", "All time", 10)
            
            # Category filter
            category_options = ["All Categories"] + categories
            category_filter = st.selectbox("🏷️ Category", category_options, index=0)
            
            # Source filter
            source_options = ["All Sources"] + sorted(sources)
            source_filter = st.selectbox("📰 Source", source_options, index=0)
            
            # Article limit
            article_limit = st.slider("📊 Articles to Show", min_value=50, max_value=200, value=200, step=50)
            
            # Show stats
            st.markdown("### 📈 Statistics")
            st.markdown(f'<div class="metric-container">', unsafe_allow_html=True)
            st.metric("Total Articles", stats['total_articles'])
            st.metric("Last 24 Hours", stats['recent_articles_24h'])
            st.markdown('</div>', unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Error loading data: {e}")
            st.stop()
    
    # Main content area
    col1, col2 = st.columns([3, 1])
    
    with col2:
        if st.button("🔄 Refresh Articles", type="primary"):
            st.cache_data.clear()
            st.rerun()
    
    with col1:
        st.markdown(f"### Latest Articles ({time_filter})")
    
    # Auto-refresh logic
    if auto_refresh:
        time.sleep(30)
        st.rerun()
    
    # Load articles
    try:
        articles, stats, sources, categories = get_articles_data(category_filter, source_filter, time_filter, article_limit)
        
        if not articles:
            st.warning("No articles found matching the current filters. Try adjusting your filter criteria.")
            return
        
        # Display articles
        for article in articles:
            with st.container():
                st.markdown('<div class="article-card">', unsafe_allow_html=True)
                
                # Title
                st.markdown(f'<div class="article-title">{article["title"]}</div>', unsafe_allow_html=True)
                
                # Meta information
                time_ago = format_time_ago(article.get('published_date'))
                st.markdown(
                    f'<div class="article-meta">'
                    f'<span class="article-source">{article["source"]}</span> • '
                    f'{time_ago} • '
                    f'<span class="article-category">{article.get("category", "Uncategorized")}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                
                # Description
                if article.get('description'):
                    description = article['description'][:200] + "..." if len(article['description']) > 200 else article['description']
                    st.markdown(f'<div class="article-description">{description}</div>', unsafe_allow_html=True)
                
                # Read more button
                st.markdown(
                    f'<a href="{article["url"]}" target="_blank" class="read-more-btn">Read Full Article →</a>',
                    unsafe_allow_html=True
                )
                
                st.markdown('</div>', unsafe_allow_html=True)
                
        # Pagination info
        st.markdown(f"---")
        st.markdown(f"**Showing {len(articles)} articles** (filtered from {stats['total_articles']} total)")
        
        # Category breakdown
        if stats.get('by_category'):
            st.markdown("### 📊 Articles by Category")
            category_df = pd.DataFrame([
                {"Category": cat, "Count": count} 
                for cat, count in stats['by_category'].items()
            ])
            st.bar_chart(category_df.set_index('Category'), use_container_width=True)
            
    except Exception as e:
        st.error(f"Error displaying articles: {e}")
        st.markdown("Please try refreshing the page or contact support if the issue persists.")

if __name__ == "__main__":
    main()