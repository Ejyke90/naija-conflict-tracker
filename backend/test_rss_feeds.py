#!/usr/bin/env python3
"""
Test RSS feeds from Nigerian news sources
"""

import feedparser
import requests

def test_rss_feeds():
    """Test that RSS feeds are accessible"""
    
    feeds = [
        "https://punchng.com/feed/",
        "https://www.vanguardngr.com/feed/",
        "https://www.premiumtimesng.com/feed/",
        "https://dailytrust.com/feed/",
        "https://www.thecable.ng/feed/",
        "https://dailynigerian.com/feed/",
        "https://leadership.ng/feed/"
    ]
    
    print("Testing RSS feeds...\n")
    
    for feed_url in feeds:
        try:
            print(f"Testing: {feed_url}")
            
            # Fetch feed
            response = requests.get(feed_url, timeout=10)
            response.raise_for_status()
            
            # Parse feed
            feed = feedparser.parse(response.content)
            
            if feed.bozo:
                print(f"  ⚠️  Warning: {feed.bozo_exception}")
            
            entries = len(feed.entries)
            print(f"  ✅ Success: {entries} articles found")
            
            # Show latest article
            if entries > 0:
                latest = feed.entries[0]
                print(f"  Latest: {latest.title[:50]}...")
            
        except Exception as e:
            print(f"  ❌ Failed: {e}")
        
        print()
    
    return True

if __name__ == "__main__":
    test_rss_feeds()
