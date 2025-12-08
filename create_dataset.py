import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# 1. Configuration
RECORD_COUNT = 10000  # Generate 10,000 data points
START_DATE = datetime.now() - timedelta(days=30) # Start from 30 days ago

# Road Segments (Using English IDs for consistency)
road_segments = ["E5-Bridge", "Tem-Kavacik", "Besiktas-Coast", "Kadikoy-Center"]

data = []

print("⏳ Generating historical traffic data... Please wait.")

# 2. Data Generation Loop
for i in range(RECORD_COUNT):
    # Increment time by 5 minutes for each record
    current_time = START_DATE + timedelta(minutes=i*5)
    hour = current_time.hour
    
    road = random.choice(road_segments)
    
    # 3. Logic: Rush Hour Simulation
    # Morning (07-09) and Evening (17-19) are busy
    if (7 <= hour <= 9) or (17 <= hour <= 19):
        # High traffic: Low speed, High density
        speed = random.randint(10, 40)
        density = random.randint(7, 10) # 7-10 (Congested)
    elif (0 <= hour <= 5):
        # Night time: High speed, Low density
        speed = random.randint(80, 120)
        density = random.randint(1, 3) # 1-3 (Free flow)
    else:
        # Normal hours
        speed = random.randint(40, 90)
        density = random.randint(3, 7) # 3-7 (Moderate)

    # 4. Append to list
    data.append({
        "timestamp": current_time,
        "hour": hour,          # Feature for AI
        "road_id": road,
        "speed": speed,
        "density": density
    })

# 5. Convert to DataFrame and Save
df = pd.DataFrame(data)

# Save as CSV
file_name = "traffic_dataset.csv"
df.to_csv(file_name, index=False)

print(f"✅ Success! Dataset created: '{file_name}'")
print(f"📊 Data Preview:\n{df.head()}")