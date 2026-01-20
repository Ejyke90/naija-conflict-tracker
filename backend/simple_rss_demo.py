#!/usr/bin/env python3
"""
Simplified Working Example: RSS-Based Naija Conflict Tracker

This demonstrates the complete workflow using the actual project structure.

Run: python simple_rss_demo.py
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
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main execution flow using project modules."""
    
    print(f"\n{'='*70}")
    print(f"  NAIJA CONFLICT TRACKER - RSS DEMO")
    print(f"{'='*70}\n")
    
    # ============================================================================
    # STEP 1: Import RSS Scraper
    # ============================================================================
    print("📡 Step 1: Importing RSS scraper...")
    
    try:
        sys.path.append('.')
        from app.nlp.rss_scraper_adapter import TargetedNewsScraper
        print("✓ RSS scraper imported successfully\n")
    except ImportError as e:
        print(f"❌ Could not import RSS scraper: {e}")
        print("Make sure you're in the backend directory")
        return
    
    # ============================================================================
    # STEP 2: Initialize Scraper
    # ============================================================================
    print("🔄 Step 2: Initializing RSS scraper...")
    scraper = TargetedNewsScraper()
    print("✓ RSS scraper initialized\n")
    
    # ============================================================================
    # STEP 3: Define Sources (as used by pipeline)
    # ============================================================================
    print("📰 Step 3: Configuring sources...")
    
    sources = [
        {'url': 'https://punchng.com', 'source_name': 'Punch', 'region': 'nigerian'},
        {'url': 'https://www.vanguardngr.com', 'source_name': 'Vanguard', 'region': 'nigerian'},
        {'url': 'https://www.premiumtimesng.com', 'source_name': 'Premium Times', 'region': 'nigerian'},
        {'url': 'https://dailytrust.com', 'source_name': 'Daily Trust', 'region': 'nigerian'},
        {'url': 'https://dailypost.ng', 'source_name': 'Daily Post', 'region': 'nigerian'},
    ]
    
    print(f"✓ Configured {len(sources)} Nigerian sources\n")
    
    # ============================================================================
    # STEP 4: Fetch Articles
    # ============================================================================
    print("🔄 Step 4: Fetching articles from RSS feeds...")
    print("(Using RSS - no 403 errors!)\n")
    
    articles = scraper.scrape_multiple_sources(sources, max_articles=20)
    
    if not articles:
        print("❌ No articles fetched")
        return
    
    # ============================================================================
    # STEP 5: Analyze Results
    # ============================================================================
    print(f"\n📊 Step 5: Results Analysis...")
    
    conflict_articles = [a for a in articles if a.get('is_conflict_related', False)]
    
    print(f"  Total articles: {len(articles)}")
    print(f"  Conflict-related: {len(conflict_articles)}")
    print(f"  Success rate: {len(articles)/len(sources)*100:.1f}%\n")
    
    # Show sample articles
    print("📰 Sample Articles:\n")
    for i, article in enumerate(articles[:5], 1):
        conflict_tag = "🔴" if article.get('is_conflict_related') else "  "
        print(f"{i}. {conflict_tag} [{article['source']}]")
        print(f"   {article['title'][:70]}...")
        print()
    
    # ============================================================================
    # STEP 6: Save Results
    # ============================================================================
    print("💾 Step 6: Saving results...")
    
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    
    # Save articles
    articles_file = output_dir / f"rss_articles_{timestamp}.json"
    with open(articles_file, 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"✓ Saved to: {articles_file}")
    
    # Save summary
    summary = {
        'timestamp': datetime.utcnow().isoformat(),
        'sources': len(sources),
        'articles': len(articles),
        'conflict_articles': len(conflict_articles),
        'by_source': {}
    }
    
    for article in articles:
        source = article['source']
        if source not in summary['by_source']:
            summary['by_source'][source] = 0
        summary['by_source'][source] += 1
    
    summary_file = output_dir / f"rss_summary_{timestamp}.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    print(f"✓ Summary saved to: {summary_file}")
    
    # ============================================================================
    # FINAL SUMMARY
    # ============================================================================
    print(f"\n{'='*70}")
    print(f"  RSS DEMO COMPLETE!")
    print(f"{'='*70}")
    print(f"\n✅ Successfully fetched {len(articles)} articles using RSS feeds")
    print(f"🔴 Found {len(conflict_articles)} conflict-related articles")
    print(f"\n📁 Check the 'output' directory for saved results")
    
    print(f"\n💡 Next steps:")
    print(f"  1. Set GROQ_API_KEY to enable NLP extraction")
    print(f"  2. Run the full pipeline with: python -m app.nlp.pipeline")
    print(f"  3. Check GitHub Actions for automated runs\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
