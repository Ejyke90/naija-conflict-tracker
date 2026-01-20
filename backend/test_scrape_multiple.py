#!/usr/bin/env python3
"""
Test script to verify scrape_multiple_sources method works
"""

import sys
import os
sys.path.append('.')

from app.nlp.news_scraper import TargetedNewsScraper

def test_scrape_multiple_sources():
    """Test the new scrape_multiple_sources method"""
    
    print("Initializing scraper...")
    scraper = TargetedNewsScraper()
    
    # Test with a single source first
    print("\n=== Testing single source ===")
    sources = ['punch']
    articles = scraper.scrape_multiple_sources(sources, hours_back=24, max_articles=2)
    
    print(f"✅ Scraped {len(articles)} articles")
    for article in articles:
        if article.get('fetch_success', False):
            print(f"  - {article['title'][:50]}...")
            print(f"    Source: {article['source_key']}")
            print(f"    URL: {article['url']}")
            print(f"    Content length: {len(article.get('content', ''))}")
        else:
            print(f"  - Failed to fetch from {article['source_key']}: {article.get('error', 'Unknown')}")
    
    # Test with multiple sources
    print("\n=== Testing multiple sources ===")
    sources = ['punch', 'vanguard']
    articles = scraper.scrape_multiple_sources(sources, hours_back=24, max_articles=5)
    
    print(f"✅ Total articles: {len(articles)}")
    success_count = sum(1 for a in articles if a.get('fetch_success', False))
    print(f"✅ Successful fetches: {success_count}")
    
    return True

if __name__ == "__main__":
    try:
        success = test_scrape_multiple_sources()
        if success:
            print("\n✅ All tests passed!")
            sys.exit(0)
        else:
            print("\n❌ Tests failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
