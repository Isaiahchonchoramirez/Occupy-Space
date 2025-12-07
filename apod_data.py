"""
APOD API Data Collection
Collects Astronomy Picture of the Day data from NASA's APOD API
Stores data in SQLite database with 25 items per run
Author: Sajjad Majeed
"""

import requests
import sqlite3
from datetime import datetime, timedelta

# NASA API key
API_KEY = "Me4x3nRxIMDsx1RPwXwfYzuLoIosBLHIt28pMdd5"
BASE_URL = "https://api.nasa.gov/planetary/apod"

def create_apod_table():
    """
    Creates the APOD images table in the database.
    Stores one entry per date with image details.
    """
    conn = sqlite3.connect('space_data.db')
    cur = conn.cursor()
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS apod_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE,
            title TEXT,
            explanation TEXT,
            url TEXT,
            media_type TEXT,
            copyright TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def get_last_apod_date():
    """
    Gets the last date we fetched APOD data for.
    Returns None if no data exists yet.
    """
    conn = sqlite3.connect('space_data.db')
    cur = conn.cursor()
    
    cur.execute('SELECT MAX(date) FROM apod_images')
    result = cur.fetchone()[0]
    
    conn.close()
    
    if result:
        return datetime.strptime(result, '%Y-%m-%d')
    return None

def fetch_apod_data(date):
    """
    Fetches APOD data for a specific date.
    Returns JSON data or None if error.
    """
    params = {
        'date': date.strftime('%Y-%m-%d'),
        'api_key': API_KEY
    }
    
    response = requests.get(BASE_URL, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error for {date.strftime('%Y-%m-%d')}: {response.status_code}")
        return None

def store_apod_data(data):
    """
    Stores a single APOD entry in the database.
    Returns True if successful, False if duplicate or error.
    """
    if not data:
        return False
    
    conn = sqlite3.connect('space_data.db')
    cur = conn.cursor()
    
    try:
        cur.execute('''
            INSERT INTO apod_images 
            (date, title, explanation, url, media_type, copyright)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data['date'],
            data['title'],
            data['explanation'],
            data['url'],
            data['media_type'],
            data.get('copyright', 'Public Domain')
        ))
        
        conn.commit()
        conn.close()
        return True
        
    except sqlite3.IntegrityError:
        # Duplicate entry
        conn.close()
        return False

def count_space_keywords(explanation):
    """
    Helper function to count space-related keywords in APOD explanations.
    Used for correlation analysis with NEO data.
    """
    keywords = ['asteroid', 'meteor', 'comet', 'space', 'galaxy', 'nebula', 'star']
    explanation_lower = explanation.lower()
    
    counts = {}
    for keyword in keywords:
        counts[keyword] = explanation_lower.count(keyword)
    
    return counts

def main():
    """
    Main function - fetches and stores APOD data incrementally.
    Each run gets up to 25 daily entries.
    """
    print("=" * 50)
    print("APOD Data Collection")
    print("=" * 50)
    
    # Create table if it doesn't exist
    create_apod_table()
    
    # Determine starting date
    last_date = get_last_apod_date()
    
    if last_date:
        start_date = last_date + timedelta(days=1)
        print(f"Last fetch date: {last_date.strftime('%Y-%m-%d')}")
    else:
        # Start from same date as NEO data for correlation analysis
        start_date = datetime(2024, 1, 1)
        print("First run - starting from 2024-01-01")
    
    # Fetch up to 25 entries
    items_added = 0
    current_date = start_date
    max_items = 25
    
    print(f"Fetching APOD data starting from {start_date.strftime('%Y-%m-%d')}")
    
    while items_added < max_items:
        # Don't fetch future dates
        if current_date > datetime.now():
            print("Reached current date - no more data available")
            break
        
        data = fetch_apod_data(current_date)
        
        if data:
            if store_apod_data(data):
                items_added += 1
                print(f"✓ Added: {current_date.strftime('%Y-%m-%d')} - {data['title'][:50]}...")
            else:
                print(f"- Skipped: {current_date.strftime('%Y-%m-%d')} (duplicate)")
        
        current_date += timedelta(days=1)
    
    # Show current totals
    conn = sqlite3.connect('space_data.db')
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM apod_images')
    total_apod = cur.fetchone()[0]
    conn.close()
    
    print(f"\n✓ Successfully added {items_added} APOD entries")
    print(f"Total APOD entries in database: {total_apod}")
    print("\nRun this script again to fetch more data!")
    print("=" * 50)

if __name__ == "__main__":
    main()