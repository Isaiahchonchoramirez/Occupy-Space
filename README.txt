OCCUPY SPACE - Final Project
=============================
Authors: Isaiah Ramirez & Sajjad Majeed
Course: SI 201 Final Project
GitHub Repository:https://github.com/saj30/Occupy-Space.git
PROJECT DESCRIPTION
-------------------
This project analyzes Near Earth Object (NEO) asteroid data and correlates it 
with NASA's Astronomy Picture of the Day (APOD) to understand patterns in 
asteroid approaches and their coverage in space media.

FILES INCLUDED
--------------
1. neoWs_data.py      - Collects NEO asteroid data (Isaiah Ramirez)
2. apod_data.py       - Collects APOD image data (Sajjad Majeed)
3. calculations.py    - Performs analysis and creates visualizations (Both)
4. space_data.db      - SQLite database (auto-generated)
5. README.txt         - This file

REQUIRED LIBRARIES
------------------
Install these libraries before running:

pip install requests
pip install matplotlib
pip install seaborn
pip install pandas

If you are running this on Mac:

pip3 install requests
pip3 install matplotlib
pip3 install seaborn
pip3 install pandas

SETUP INSTRUCTIONS
------------------
1. Get a NASA API Key (FREE):
   - Visit: https://api.nasa.gov/
   - Enter your name and email
   - Copy your API key
   
2. Update API keys in both Python files:
   - Open neoWs_data.py
   - Replace API_KEY = "DEMO_KEY" with your key
   - Open apod_data.py
   - Replace API_KEY = "DEMO_KEY" with your key

RUNNING THE PROJECT
-------------------
IMPORTANT: You must run the data collection scripts MULTIPLE TIMES to gather
at least 100 items from each API (project requirement).

Step 1: Collect NEO Data (Run 5+ times)
   python neoWs_data.py
   
   Each run adds up to 25 asteroids. Run at least 5 times to get 100+.
   The script tracks progress and won't add duplicates.

Step 2: Collect APOD Data (Run 5+ times)
   python apod_data.py
   
   Each run adds up to 25 APOD entries. Run at least 5 times to get 100+.
   The script tracks progress and won't add duplicates.

Step 3: Run Analysis (After collecting enough data)
   python calculations.py
   
   This will:
   - Perform 3 calculations on the data
   - Create 3 visualization PNG files
   - Print results to console

EXPECTED OUTPUT
---------------
After running calculations.py, you should see:
- viz1_approaches_over_time.png
- viz2_velocity_vs_distance.png
- viz3_apod_content_analysis.png

Plus detailed statistics printed to the console.

DATABASE STRUCTURE
------------------
Table: asteroids
- id (PRIMARY KEY)
- neo_id (UNIQUE)
- name
- absolute_magnitude
- estimated_diameter_min
- estimated_diameter_max
- is_potentially_hazardous

Table: approaches (linked to asteroids via asteroid_id)
- id (PRIMARY KEY)
- asteroid_id (FOREIGN KEY)
- approach_date
- miss_distance_km
- velocity_kmh
- orbiting_body

Table: apod_images
- id (PRIMARY KEY)
- date (UNIQUE)
- title
- explanation
- url
- media_type
- copyright

CALCULATIONS PERFORMED
----------------------
1. Approaches by Day - counts asteroid approaches daily with hazard analysis
2. Velocity vs Distance - analyzes relationship between speed and proximity
3. Asteroid Size Distribution - groups asteroids by size with hazard patterns
4. APOD Keyword Analysis - tracks space object mentions in APOD posts

VISUALIZATIONS CREATED
----------------------
1. Line chart: Asteroid approaches over time (daily with moving average)
2. Scatter plot: Velocity vs miss distance (colored by hazard status, sized by diameter)
3. Pie charts: APOD content analysis (space object mentions & media types)
