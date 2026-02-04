import feedparser
import json
import os

# Load feeds
with open('data/feeds.json', 'r', encoding='utf-8') as f:
    feeds = json.load(f)

print(f"Testing {len(feeds)} feeds...")

for feed in feeds:
    print(f"\nTesting: {feed['name']} ({feed['url']})")
    try:
        d = feedparser.parse(feed['url'])
        print(f"  - Status: {d.get('status', 'Unknown')}")
        print(f"  - Entries found: {len(d.entries)}")
        if d.entries:
            print(f"  - First entry title: {d.entries[0].title}")
            print(f"  - First entry date: {d.entries[0].get('published', 'No date')}")
        else:
            print("  - NO ENTRIES FOUND. (Likely not a valid RSS feed or blocked)")
            if d.get('bozo', 0):
                 print(f"  - Parse Error (bozo): {d.bozo_exception}")
    except Exception as e:
        print(f"  - EXCEPTION: {e}")
