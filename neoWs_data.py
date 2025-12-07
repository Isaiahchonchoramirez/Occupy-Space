"""
NeoWs API Data Collection
Collects Near Earth Object asteroid data from NASA's NeoWs API
Stores data in SQLite database with 25 items per run
Author: Isaiah Ramirez
"""

import requests
import sqlite3
import json
from datetime import datetime, timedelta

# NASA API key 
API_KEY = "Me4x3nRxIMDsx1RPwXwfYzuLoIosBLHIt28pMdd5"  
BASE_URL = "https://api.nasa.gov/neo/rest/v1/feed"

def create_tables():
    """
    Creates two tables in the database:
    - asteroids: main asteroid data
    - approaches: detailed approach data (shares asteroid_id with asteroids table)
    """
    conn = sqlite3.connect('space_data.db')
    cur = conn.cursor()
    
    # Main asteroids table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS asteroids (
            id INTEGER PRIMARY KEY,
            neo_id TEXT UNIQUE,
            name TEXT,
            absolute_magnitude REAL,
            estimated_diameter_min REAL,
            estimated_diameter_max REAL,
            is_potentially_hazardous INTEGER
        )
    ''')
    
    # Approach data table (linked to asteroids via asteroid_id)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS approaches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asteroid_id INTEGER,
            approach_date TEXT,
            miss_distance_km REAL,
            velocity_kmh REAL,
            orbiting_body TEXT,
            FOREIGN KEY (asteroid_id) REFERENCES asteroids(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_last_fetch_date():
    """
    Gets the last date we fetched data for.
    Returns None if no data exists yet.
    """
    conn = sqlite3.connect('space_data.db')
    cur = conn.cursor()
    
    cur.execute('SELECT MAX(approach_date) FROM approaches')
    result = cur.fetchone()[0]
    
    conn.close()
    
    if result:
        return datetime.strptime(result, '%Y-%m-%d')
    return None

def fetch_neo_data(start_date, end_date):
    """
    Fetches NEO data from NASA API for a date range.
    API returns all asteroids approaching Earth in that date range.
    """
    params = {
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'api_key': API_KEY
    }
    
    response = requests.get(BASE_URL, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None

def store_neo_data(data):
    """
    Stores NEO data in database, limiting to 25 new items per run.
    Avoids duplicates by checking neo_id.
    Returns number of items added.
    """
    if not data or 'near_earth_objects' not in data:
        return 0
    
    conn = sqlite3.connect('space_data.db')
    cur = conn.cursor()
    
    items_added = 0
    max_items = 25
    
    # Process each date's asteroids
    for date_key in data['near_earth_objects']:
        if items_added >= max_items:
            break
            
        asteroids = data['near_earth_objects'][date_key]
        
        for asteroid in asteroids:
            if items_added >= max_items:
                break
            
            neo_id = asteroid['id']
            
            # Check if asteroid already exists
            cur.execute('SELECT id FROM asteroids WHERE neo_id = ?', (neo_id,))
            existing = cur.fetchone()
            
            if existing:
                asteroid_id = existing[0]
            else:
                # Insert new asteroid
                cur.execute('''
                    INSERT INTO asteroids 
                    (neo_id, name, absolute_magnitude, estimated_diameter_min, 
                     estimated_diameter_max, is_potentially_hazardous)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    neo_id,
                    asteroid['name'],
                    asteroid['absolute_magnitude_h'],
                    asteroid['estimated_diameter']['kilometers']['estimated_diameter_min'],
                    asteroid['estimated_diameter']['kilometers']['estimated_diameter_max'],
                    1 if asteroid['is_potentially_hazardous_asteroid'] else 0
                ))
                asteroid_id = cur.lastrowid
                items_added += 1
            
            # Store approach data (can have multiple approaches per asteroid)
            for approach in asteroid['close_approach_data']:
                approach_date = approach['close_approach_date']
                
                # Check if this specific approach already exists
                cur.execute('''
                    SELECT id FROM approaches 
                    WHERE asteroid_id = ? AND approach_date = ?
                ''', (asteroid_id, approach_date))
                
                if not cur.fetchone():
                    cur.execute('''
                        INSERT INTO approaches 
                        (asteroid_id, approach_date, miss_distance_km, 
                         velocity_kmh, orbiting_body)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        asteroid_id,
                        approach_date,
                        float(approach['miss_distance']['kilometers']),
                        float(approach['relative_velocity']['kilometers_per_hour']),
                        approach['orbiting_body']
                    ))
    
    conn.commit()
    conn.close()
    
    return items_added

def main():
    """
    Main function - fetches and stores NEO data incrementally.
    Each run gets data for 7 days and stores up to 25 items.
    """
    print("=" * 50)
    print("NeoWs Data Collection")
    print("=" * 50)
    
    # Create tables if they don't exist
    create_tables()
    
    # Determine date range to fetch
    last_date = get_last_fetch_date()
    
    if last_date:
        start_date = last_date + timedelta(days=1)
        print(f"Last fetch date: {last_date.strftime('%Y-%m-%d')}")
    else:
        # Start from a date with good data
        start_date = datetime(2024, 1, 1)
        print("First run - starting from 2024-01-01")
    
    end_date = start_date + timedelta(days=6)  # 7-day range (API limit)
    
    print(f"Fetching data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    # Fetch data from API
    data = fetch_neo_data(start_date, end_date)
    
    if data:
        items_added = store_neo_data(data)
        print(f"✓ Successfully added {items_added} items to database")
        
        # Show current totals
        conn = sqlite3.connect('space_data.db')
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM asteroids')
        total_asteroids = cur.fetchone()[0]
        cur.execute('SELECT COUNT(*) FROM approaches')
        total_approaches = cur.fetchone()[0]
        conn.close()
        
        print(f"Total asteroids in database: {total_asteroids}")
        print(f"Total approaches in database: {total_approaches}")
        print("\nRun this script again to fetch more data!")
    else:
        print("Failed to fetch data from API")
    
    print("=" * 50)

if __name__ == "__main__":
    main()