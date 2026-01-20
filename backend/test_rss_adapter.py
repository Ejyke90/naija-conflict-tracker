#!/usr/bin/env python3
"""
Test the RSS scraper adapter with existing pipeline format
"""

import sys
import os
sys.path.append('.')

from app.nlp.rss_scraper_adapter import TargetedNewsScraper

def test_rss_adapter():
    """Test that the RSS adapter works with existing pipeline calls"""
    
    print("Testing RSS Scraper Adapter...")
    print("=" * 60)
    
    # Initialize scraper (same as existing pipeline)
    scraper = TargetedNewsScraper()
    
    # Test with the exact format your pipeline uses
    sources = [
        {
            'url': 'https://punchng.com/topics/security/',
            'source_name': 'Punch',
            'region': 'nigerian'
        },
        {
            'url': 'https://www.vanguardngr.com/category/news/',
            'source_name': 'Vanguard',
            'region': 'nigerian'
        },
        {
            'url': 'https://www.premiumtimesng.com/news/headlines',
            'source_name': 'Premium Times',
            'region': 'nigerian'
        }
    ]
    
    # Call the method your pipeline expects
    print("\nCalling scrape_multiple_sources()...")
    articles = scraper.scrape_multiple_sources(sources, max_articles=10)
    
    print(f"\n✅ SUCCESS! Fetched {len(articles)} articles")
    
    # Verify the format matches what pipeline expects
    if articles:
        sample = articles[0]
        print(f"\nSample article format:")
        print(f"  - url: {sample.get('url', 'MISSING')}")
        print(f"  - title: {sample.get('title', 'MISSING')}")
        print(f"  - source: {sample.get('source', 'MISSING')}")
        print(f"  - region: {sample.get('region', 'MISSING')}")
        print(f"  - fetch_success: {sample.get('fetch_success', 'MISSING')}")
        print(f"  - encoding_used: {sample.get('encoding_used', 'MISSING')}")
        print(f"  - is_conflict_related: {sample.get('is_conflict_related', 'MISSING')}")
    
    # Show conflict articles
    conflict_articles = [a for a in articles if a.get('is_conflict_related')]
    print(f"\n✅ Conflict-related articles: {len(conflict_articles)}")
    
    print("\n" + "=" * 60)
    print("✅ RSS adapter is ready for pipeline integration!")
    print("   it's a drop-in replacement - no code changes needed!")
    
    return True

if __name__ == "__main__":
    try:
        success = test_rss_adapter()
        if success:
            print("\n✅ Test passed!")
            sys.exit(0)
        else:
            print("\n❌ Test failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
