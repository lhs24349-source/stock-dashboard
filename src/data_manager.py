import json
import os
import feedparser
import pandas as pd
from datetime import datetime
import time

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
FEEDS_FILE = os.path.join(DATA_DIR, 'feeds.json')
NEWS_FILE = os.path.join(DATA_DIR, 'news.json')
STATS_FILE = os.path.join(DATA_DIR, 'stats.json')

class DataManager:
    def __init__(self):
        self._ensure_files()

    def _ensure_files(self):
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        if not os.path.exists(FEEDS_FILE):
            with open(FEEDS_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f)
        if not os.path.exists(NEWS_FILE):
            with open(NEWS_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f)
        if not os.path.exists(STATS_FILE):
            with open(STATS_FILE, 'w', encoding='utf-8') as f:
                json.dump({"visitors": 0}, f)

    def get_feeds(self):
        with open(FEEDS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)

    def add_feed(self, name, url, category):
        feeds = self.get_feeds()
        new_feed = {"name": name, "url": url, "category": category}
        feeds.append(new_feed)
        with open(FEEDS_FILE, 'w', encoding='utf-8') as f:
            json.dump(feeds, f, indent=4, ensure_ascii=False)
        return True

    def remove_feed(self, url):
        feeds = self.get_feeds()
        feeds = [f for f in feeds if f['url'] != url]
        with open(FEEDS_FILE, 'w', encoding='utf-8') as f:
            json.dump(feeds, f, indent=4, ensure_ascii=False)
        return True

    def fetch_and_update_news(self):
        from dateutil import parser as date_parser
        
        feeds = self.get_feeds()
        existing_news = self.load_news()
        existing_links = {item['link'] for item in existing_news}
        
        new_items = []
        for feed in feeds:
            try:
                parsed = feedparser.parse(feed['url'])
                if not parsed.entries:
                    print(f"Warning: No entries for {feed['name']}")
                    continue
                    
                for entry in parsed.entries:
                    if entry.link not in existing_links:
                        # Attempt to parse date
                        raw_date = entry.get('published', datetime.now().isoformat())
                        try:
                            dt = date_parser.parse(raw_date)
                            # Convert to naive or UTC to avoid mixing offset-aware/naive
                            published_iso = dt.isoformat()
                        except:
                            published_iso = datetime.now().isoformat()
                        
                        item = {
                            'title': entry.title,
                            'link': entry.link,
                            'summary': entry.get('summary', ''),
                            'published': published_iso,
                            'source': feed['name'],
                            'category': feed['category'],
                            'fetched_at': datetime.now().isoformat()
                        }
                        new_items.append(item)
                        existing_links.add(entry.link)
            except Exception as e:
                print(f"Error fetching {feed['url']}: {e}")
        
        # Combine
        all_news = new_items + existing_news
        
        # Sort by 'published' date descending
        try:
            all_news.sort(key=lambda x: x.get('published', ''), reverse=True)
        except:
             pass # Fallback if sorting fails
             
        # Keep only last 30 days or max 1000 items
        all_news = all_news[:1000]
        
        with open(NEWS_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_news, f, indent=4, ensure_ascii=False)
        
        return len(new_items)

    def load_news(self):
        try:
            with open(NEWS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def load_stats(self):
        try:
            with open(STATS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"visitors": 0}

    def increment_visitor_count(self):
        stats = self.load_stats()
        stats["visitors"] += 1
        with open(STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(stats, f)
        return stats["visitors"]
