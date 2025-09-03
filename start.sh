#!/bin/bash

# Fashion & Beauty News Aggregator - Start Script

echo "🚀 Starting Fashion & Beauty News Aggregator..."

# Activate virtual environment
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found. Run setup first."
    exit 1
fi

# Check if database exists and has data
if [ ! -f "articles.db" ]; then
    echo "📊 Database not found. Running initial aggregation..."
    python -c "
from src.aggregator import NewsAggregator
import sys
try:
    agg = NewsAggregator()
    print(f'📡 Fetching from {len(agg.feeds)} sources...')
    new = agg.fetch_all_feeds()
    stats = agg.get_stats()
    print(f'✅ Initial aggregation complete:')
    print(f'   📰 {new} new articles loaded')
    print(f'   📊 {stats[\"total_articles\"]} total articles in database')
    print(f'   ⏰ {stats[\"recent_articles_24h\"]} articles from last 24h')
except Exception as e:
    print(f'⚠️  Warning: Initial aggregation failed: {e}')
    print('   App will start anyway with empty database')
"
fi

# Start Streamlit app
echo "🌐 Starting Streamlit dashboard..."
echo "📍 App will be available at: http://localhost:8501"
echo "🔄 Auto-refresh enabled for live updates"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

streamlit run app.py --server.headless=true