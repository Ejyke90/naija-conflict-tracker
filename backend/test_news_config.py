#!/usr/bin/env python3
"""
Test script to verify news sources configuration
"""

import json
import os
from pathlib import Path

def test_news_config():
    """Test loading and validating news sources configuration"""
    
    # Load config
    config_path = Path(__file__).parent / "config" / "news_sources.json"
    
    if not config_path.exists():
        print(f"❌ Config file not found at {config_path}")
        return False
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    print("✅ Configuration loaded successfully")
    
    # Validate structure
    assert 'sources' in config, "Missing 'sources' key"
    assert 'config' in config, "Missing 'config' key"
    
    # Check sources
    active_sources = [s for s in config['sources'] if s.get('active', False)]
    print(f"✅ Found {len(active_sources)} active sources")
    
    # Print active sources
    for source in active_sources:
        print(f"  - {source['name']}: {len(source['urls'])} URLs")
    
    # Check config
    fetch_config = config['config']['fetch_settings']
    extraction_config = config['config']['extraction_settings']
    
    print(f"\n✅ Fetch settings:")
    print(f"  - Timeout: {fetch_config['timeout']}s")
    print(f"  - Retry attempts: {fetch_config['retry_attempts']}")
    print(f"  - Delay: {fetch_config['delay_between_requests']}s")
    
    print(f"\n✅ Extraction settings:")
    print(f"  - Model: {extraction_config['groq_model']}")
    print(f"  - Temperature: {extraction_config['temperature']}")
    print(f"  - Max tokens: {extraction_config['max_tokens']}")
    
    return True

if __name__ == "__main__":
    success = test_news_config()
    exit(0 if success else 1)
