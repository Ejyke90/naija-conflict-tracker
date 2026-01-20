#!/usr/bin/env python3
"""
Test the RSS News Fetcher
"""

import sys
import os
sys.path.append('.')

from app.nlp.rss_fetcher import RSSNewsFetcher

def test_rss_fetcher():
    """Test the RSS fetcher with real feeds"""
    
    print("Initializing RSS Fetcher...")
    fetcher = RSSNewsFetcher()
    
    # Load previously seen articles
    fetcher.load_seen_guids()
    
    print("\n=== Testing Tier 1 Feeds (Fastest) ===")
    # Test with just priority 1 feeds
    articles = fetcher.fetch_all_feeds(
        max_priority=1,
        delay_between=0.5
    )
    
    print(f"\n✅ Total articles fetched: {len(articles)}")
    
    # Show conflict articles
    conflict_articles = [a for a in articles if a.get('is_conflict_related')]
    print(f"✅ Conflict-related articles: {len(conflict_articles)}")
    
    # Show sample articles
    print("\n=== Sample Articles ===")
    for article in articles[:5]:
        conflict_tag = "🔴" if article.get('is_conflict_related') else "  "
        print(f"{conflict_tag} {article['source']}: {article['title'][:60]}...")
        print(f"    {article['published_date'][:10]}")
    
    # Save seen GUIDs
    fetcher.save_seen_guids()
    
    return True

if __name__ == "__main__":
    try:
        success = test_rss_fetcher()
        if success:
            print("\n✅ RSS Fetcher test completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ RSS Fetcher test failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
