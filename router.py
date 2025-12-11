import networkx as nx
import time
import redis
import random

redis_client = redis.Redis(host='localhost', port=6379, db=0)

G = nx.DiGraph() 

intersections = ["A (Levent)", "B (Besiktas)", "C (Kavacik)", "D (Kadikoy)", "E (Atasehir)"]
G.add_nodes_from(intersections)

G.add_edges_from([
    ("A (Levent)", "B (Besiktas)", {'weight': 10, 'road_id': 'E5-Bridge'}),
    ("A (Levent)", "C (Kavacik)", {'weight': 25, 'road_id': 'Tem-Kavacik'}), 
    ("B (Besiktas)", "D (Kadikoy)", {'weight': 15, 'road_id': 'Besiktas-Coast'}),
    ("C (Kavacik)", "E (Atasehir)", {'weight': 10, 'road_id': 'Tem-Kavacik'}), 
    ("D (Kadikoy)", "E (Atasehir)", {'weight': 5, 'road_id': 'Kadikoy-Center'}),
    ("E (Atasehir)", "A (Levent)", {'weight': 30, 'road_id': 'E5-Bridge'}) 
])

def dynamic_cost_calculator(u, v, data):
    """
    Calculates the dynamic weight of an edge based on real-time Redis data.
    """
    road_id = data.get('road_id')
    static_duration = data.get('weight')

    redis_data = redis_client.hget(road_id, 'congestion_status')
    
    #SIMPLE ALGORITHM IS USED TO CALCULATE DURATION DYNAMICALLY
    #FIND MORE COMPLEX ONE LATER!
    if redis_data:
        congestion = redis_data.decode('utf-8')
        
        if congestion == 'LOCKED':
            penalty_factor = 3.0 
        elif congestion == 'HEAVY':
            penalty_factor = 1.5 
        else: 
            penalty_factor = 1.0 
        
        dynamic_duration = static_duration * penalty_factor
        return dynamic_duration
    else:
        return static_duration

def find_dynamic_route(start_node, target_node):
    try:
        route = nx.dijkstra_path(G, start_node, target_node, weight=dynamic_cost_calculator)
        total_duration = nx.dijkstra_path_length(G, start_node, target_node, weight=dynamic_cost_calculator)
        
        print(f"\n--- Dynamic Route Result ({time.strftime('%H:%M:%S')}) ---")
        print(f"Start: {start_node}, Target: {target_node}")
        print(f"Shortest Route: {' -> '.join(route)}")
        print(f"Estimated Duration: {total_duration:.2f} minutes")
        print("------------------------------------------------")
        return route, total_duration
        
    except nx.NetworkXNoPath:
        print(f"ERROR: No path found between {start_node} and {target_node}.")
        return None, None

print("Dynamic Route Calculator Started! (Exit: CTRL+C)")
try:
    while True:
        find_dynamic_route("A (Levent)", "E (Atasehir)")
        time.sleep(5) 
except KeyboardInterrupt:
    print("\nRoute calculator stopped.")

