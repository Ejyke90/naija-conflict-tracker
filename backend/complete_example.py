#!/usr/bin/env python3
"""
Complete Working Example: RSS-Based Naija Conflict Tracker

This demonstrates the complete workflow:
1. Fetch articles from RSS feeds (Nigerian + International)
2. Filter for Nigeria relevance
3. Extract conflict events with Groq
4. Cross-validate between sources
5. Save results

Run: python complete_example.py
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Ensure UTF-8
sys.stdout.reconfigure(encoding='utf-8')


def main():
    """Main execution flow."""
    
    print(f"\n{'='*70}")
    print(f"  NAIJA CONFLICT TRACKER - RSS-BASED PIPELINE")
    print(f"{'='*70}\n")
    
    # ============================================================================
    # STEP 1: Initialize RSS Fetcher
    # ============================================================================
    print("📡 Step 1: Initializing RSS Fetcher...")
    
    # Import your RSS fetcher (adjust import based on your file structure)
    try:
        from rss_scraper import RSSBasedScraper as TargetedNewsScraper
    except ImportError:
        logger.error("Could not import RSS scraper. Make sure rss_scraper.py exists.")
        logger.info("Creating inline version for demo...")
        # For demo purposes, we'll use a minimal version
        TargetedNewsScraper = MinimalRSSScraperDemo
    
    scraper = TargetedNewsScraper()
    print("✓ RSS Fetcher initialized\n")
    
    # ============================================================================
    # STEP 2: Define Sources
    # ============================================================================
    print("📰 Step 2: Defining news sources...")
    
    sources = [
        # Nigerian sources (Tier 1)
        {'url': 'https://punchng.com/feed/', 'source_name': 'Punch Nigeria', 'region': 'nigerian'},
        {'url': 'https://www.premiumtimesng.com/feed/', 'source_name': 'Premium Times', 'region': 'nigerian'},
        {'url': 'https://www.vanguardngr.com/feed/', 'source_name': 'Vanguard', 'region': 'nigerian'},
        {'url': 'https://dailypost.ng/feed/', 'source_name': 'Daily Post', 'region': 'nigerian'},
        {'url': 'https://www.channelstv.com/feed/', 'source_name': 'Channels TV', 'region': 'nigerian'},
        
        # International sources
        {'url': 'http://feeds.bbci.co.uk/news/world/africa/rss.xml', 'source_name': 'BBC Africa', 'region': 'international'},
        {'url': 'https://allafrica.com/tools/headlines/rdf/nigeria/headlines.rdf', 'source_name': 'AllAfrica Nigeria', 'region': 'nigerian'},
        {'url': 'https://www.africanews.com/feed/rss', 'source_name': 'Africanews', 'region': 'international'},
        {'url': 'https://www.france24.com/en/africa/rss', 'source_name': 'France 24', 'region': 'international'},
        
        # Specialized
        {'url': 'https://allafrica.com/tools/headlines/rdf/conflict/headlines.rdf', 'source_name': 'AllAfrica Conflict', 'region': 'specialized'},
    ]
    
    print(f"✓ Configured {len(sources)} sources")
    print(f"  - Nigerian: {sum(1 for s in sources if s['region'] == 'nigerian')}")
    print(f"  - International: {sum(1 for s in sources if s['region'] == 'international')}")
    print(f"  - Specialized: {sum(1 for s in sources if s['region'] == 'specialized')}\n")
    
    # ============================================================================
    # STEP 3: Fetch Articles from RSS Feeds
    # ============================================================================
    print("🔄 Step 3: Fetching articles from RSS feeds...")
    print("(This replaces web scraping - no more 403 errors!)\n")
    
    # Limit for demo (remove max_articles=20 for production)
    articles = scraper.scrape_multiple_sources(sources, max_articles=50)
    
    if not articles:
        print("\n❌ No articles fetched. Check your internet connection or RSS feed URLs.")
        return
    
    # ============================================================================
    # STEP 4: Analyze Articles
    # ============================================================================
    print(f"\n📊 Step 4: Article Analysis...")
    
    conflict_articles = [a for a in articles if a.get('is_conflict_related', False)]
    nigerian_articles = [a for a in articles if a['region'] == 'nigerian']
    intl_articles = [a for a in articles if a['region'] == 'international']
    
    print(f"  Total articles: {len(articles)}")
    print(f"  Conflict-related: {len(conflict_articles)} ({len(conflict_articles)/len(articles)*100:.1f}%)")
    print(f"  By region:")
    print(f"    • Nigerian sources: {len(nigerian_articles)}")
    print(f"    • International sources: {len(intl_articles)}")
    print(f"    • Other: {len(articles) - len(nigerian_articles) - len(intl_articles)}\n")
    
    # Show sample articles
    print("📰 Sample Articles:\n")
    for i, article in enumerate(articles[:5], 1):
        conflict_tag = "🔴" if article.get('is_conflict_related') else "  "
        region_tag = {"nigerian": "🇳🇬", "international": "🌍"}.get(article['region'], "  ")
        print(f"{i}. {conflict_tag} {region_tag} [{article['source']}]")
        print(f"   {article['title'][:65]}...")
        print(f"   {article['url'][:70]}...")
        print()
    
    # ============================================================================
    # STEP 5: Extract Events with NLP (Optional - requires GROQ_API_KEY)
    # ============================================================================
    print("\n🤖 Step 5: NLP Event Extraction...")
    
    api_key = os.getenv('GROQ_API_KEY')
    
    if not api_key:
        print("⚠️  GROQ_API_KEY not found - skipping NLP extraction")
        print("   (Set environment variable to enable event extraction)")
        events = []
    else:
        print("✓ API Key found - extracting events...")
        
        try:
            # Import your NLP extractor
            from nlp_extractor import ConflictEventExtractor
            
            extractor = ConflictEventExtractor(enable_cross_validation=True)
            
            # Extract from conflict-related articles only (faster)
            results = extractor.batch_extract(conflict_articles[:20])  # Limit for demo
            
            events = results.get('events', [])
            stats = results.get('stats', {})
            
            print(f"\n  Events extracted: {len(events)}")
            print(f"  Extraction rate: {stats.get('extraction_rate', 'N/A')}")
            
            if extractor.enable_cross_validation:
                cv_stats = stats.get('cross_validation', {})
                print(f"  Cross-validation:")
                print(f"    • Dual-validated (local+intl): {cv_stats.get('dual_validated', 0)}")
                print(f"    • Internationally validated: {cv_stats.get('internationally_validated', 0)}")
                print(f"    • Locally validated: {cv_stats.get('locally_validated', 0)}")
            
        except ImportError:
            print("⚠️  NLP extractor not found - skipping")
            events = []
        except Exception as e:
            print(f"⚠️  NLP extraction failed: {e}")
            events = []
    
    # ============================================================================
    # STEP 6: Save Results
    # ============================================================================
    print(f"\n💾 Step 6: Saving results...")
    
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    
    # Save articles
    articles_file = output_dir / f"articles_{timestamp}.json"
    with open(articles_file, 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"  ✓ Articles saved: {articles_file}")
    
    # Save events if any
    if events:
        events_file = output_dir / f"events_{timestamp}.json"
        with open(events_file, 'w', encoding='utf-8') as f:
            json.dump({
                'events': events,
                'extracted_at': datetime.utcnow().isoformat(),
                'total_events': len(events)
            }, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"  ✓ Events saved: {events_file}")
    
    # Save summary
    summary = {
        'timestamp': datetime.utcnow().isoformat(),
        'sources_configured': len(sources),
        'articles_fetched': len(articles),
        'conflict_articles': len(conflict_articles),
        'events_extracted': len(events),
        'by_source': {},
        'by_region': {}
    }
    
    # Count by source
    for article in articles:
        source = article['source']
        region = article['region']
        
        if source not in summary['by_source']:
            summary['by_source'][source] = 0
        summary['by_source'][source] += 1
        
        if region not in summary['by_region']:
            summary['by_region'][region] = 0
        summary['by_region'][region] += 1
    
    summary_file = output_dir / f"summary_{timestamp}.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    print(f"  ✓ Summary saved: {summary_file}")
    
    # ============================================================================
    # FINAL SUMMARY
    # ============================================================================
    print(f"\n{'='*70}")
    print(f"  PIPELINE COMPLETE!")
    print(f"{'='*70}")
    print(f"\n📈 Final Statistics:")
    print(f"  • Sources processed: {len(sources)}")
    print(f"  • Articles fetched: {len(articles)}")
    print(f"  • Conflict-related: {len(conflict_articles)}")
    print(f"  • Events extracted: {len(events)}")
    print(f"\n📁 Output files:")
    print(f"  • {articles_file}")
    if events:
        print(f"  • {events_file}")
    print(f"  • {summary_file}")
    
    print(f"\n✅ Success! Check the 'output' directory for results.\n")
    
    # Show sample events if any
    if events:
        print(f"\n🔍 Sample Extracted Events:\n")
        for i, event in enumerate(events[:3], 1):
            print(f"{i}. {event.get('event_type', 'Unknown')} - {event.get('location', 'Unknown location')}")
            print(f"   Date: {event.get('date', 'Unknown')}")
            print(f"   Source: {event.get('source_name', 'Unknown')}")
            if event.get('casualties'):
                cas = event['casualties']
                print(f"   Casualties: {cas.get('deaths', 0)} deaths, {cas.get('injured', 0)} injured, {cas.get('kidnapped', 0)} kidnapped")
            print(f"   {event.get('description', '')[:100]}...")
            if event.get('dual_validated'):
                print(f"   ✓ Dual-validated (local + international sources)")
            print()


# Minimal RSS scraper for demo if main one isn't available
class MinimalRSSScraperDemo:
    """Minimal RSS scraper for demonstration."""
    
    def scrape_multiple_sources(self, sources, max_articles=None):
        import feedparser
        from bs4 import BeautifulSoup
        from datetime import datetime
        
        articles = []
        
        for source in sources[:3]:  # Limit to 3 for demo
            try:
                feed = feedparser.parse(source['url'])
                for entry in feed.entries[:5]:  # 5 per feed
                    content = entry.get('summary', '')
                    if content:
                        soup = BeautifulSoup(content, 'html.parser')
                        content = soup.get_text()
                    
                    articles.append({
                        'title': entry.get('title', ''),
                        'content': content,
                        'url': entry.get('link', ''),
                        'source': source['source_name'],
                        'region': source['region'],
                        'published_date': datetime.utcnow().isoformat(),
                        'fetch_success': True,
                        'is_conflict_related': 'attack' in entry.get('title', '').lower()
                    })
            except Exception as e:
                print(f"Error fetching {source['source_name']}: {e}")
        
        return articles


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Pipeline failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
