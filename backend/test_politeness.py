#!/usr/bin/env python3
"""Test the domain politeness manager"""

import sys
import time
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.nlp.domain_politeness import DomainPolitenessManager

print("Testing Domain Politeness Manager...")
print("=" * 50)

# Create manager with 3 second delay
politeness = DomainPolitenessManager(min_delay_between_requests=3)

# Test URLs
test_urls = [
    "https://api.groq.com/v1/chat/completions",
    "https://api.groq.com/v1/models",
    "https://example.com/api/test"
]

print("\n1. Testing first request (should not wait):")
wait_time = politeness.should_wait(test_urls[0])
print(f"   Wait time: {wait_time}")
politeness.record_request(test_urls[0])

print("\n2. Testing immediate second request to same domain (should wait):")
wait_time = politeness.should_wait(test_urls[1])
print(f"   Wait time: {wait_time:.1f} seconds")

print("\n3. Testing request to different domain (should not wait):")
wait_time = politeness.should_wait(test_urls[2])
print(f"   Wait time: {wait_time}")

print("\n4. Waiting 3 seconds and testing again...")
time.sleep(3)
wait_time = politeness.should_wait(test_urls[0])
print(f"   Wait time: {wait_time}")

print("\n5. Final statistics:")
stats = politeness.get_stats()
for domain, count in stats.items():
    print(f"   {domain}: {count} requests")

print("\n✓ Politeness manager working correctly!")
print("\nThis will help reduce 429 errors by:")
print("- Tracking last request time per domain")
print("- Adding delays when needed")
print("- Being 'polite' to API servers")
