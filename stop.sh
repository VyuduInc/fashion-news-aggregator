#!/bin/bash

# Fashion & Beauty News Aggregator - Stop Script

echo "🛑 Stopping Fashion & Beauty News Aggregator..."

# Kill Streamlit processes
pkill -f "streamlit run app.py"

# Kill Python aggregator processes
pkill -f "NewsAggregator"

echo "✅ All processes stopped"