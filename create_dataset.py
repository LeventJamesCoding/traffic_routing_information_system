import pandas as pd
import numpy as np
import random
import datetime

RECORD_COUNT = 10000  
START_DATE = datetime.now() - datetime.timedelta(days=30) 

road_segments = ["E5-Bridge", "Tem-Kavacik", "Besiktas-Coast", "Kadikoy-Center"]

data = []

print("Generating historical traffic data... Please wait.")

for i in range(RECORD_COUNT):
    current_time = START_DATE + datetime.timedelta(minutes=i*5)
    hour = current_time.hour
    road = random.choice(road_segments)
    
    if (7 <= hour <= 9) or (17 <= hour <= 19):
        speed = random.randint(10, 40)
        density = random.randint(7, 10) 
    elif (0 <= hour <= 5):
        speed = random.randint(80, 120)
        density = random.randint(1, 3) 
    else:
        speed = random.randint(40, 90)
        density = random.randint(3, 7) 

    data.append({
        "timestamp": current_time,
        "hour": hour, #feature for ai
        "road_id": road,
        "speed": speed,
        "density": density
    })

df = pd.DataFrame(data)

file_name = "traffic_dataset.csv"
df.to_csv(file_name, index=False)

print(f"Success! Dataset created: '{file_name}'")
print(f"Data Preview:\n{df.head()}")