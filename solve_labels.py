# solve_labels.py
"""
Solve CVRP instances optimally using OR-Tools to generate labels.
Uses Euclidean distance with km scaling.
"""

from ortools.constraint_solver import pywrapcp, routing_enums_pb2
import json
import os
import numpy as np
import joblib

INPUT_DIR = "data/raw"
OUTPUT_DIR = "data/processed"
OUTPUT_FILE = f"{OUTPUT_DIR}/labeled_dataset.joblib"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_distance_matrix(customers, depot=(0,0)):
    locations = [depot] + customers
    n = len(locations)
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            dx = (locations[i][0] - locations[j][0]) * 111
            dy = (locations[i][1] - locations[j][1]) * 111 * np.cos(np.radians(locations[i][0]))
            dist_matrix[i][j] = int(np.hypot(dx, dy) * 100)
    return dist_matrix.astype(int).tolist()

def solve_cvrp(customers, demands, num_vehicles=3, vehicle_capacity=15):
    if any(d > vehicle_capacity for d in demands):
        return None
    if sum(demands) > num_vehicles * vehicle_capacity:
        return None

    dist_matrix = create_distance_matrix(customers)
    manager = pywrapcp.RoutingIndexManager(len(dist_matrix), num_vehicles, 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return dist_matrix[from_node][to_node]
    transit_callback = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback)

    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        if from_node == 0: return 0
        return demands[from_node - 1]
    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,
        [vehicle_capacity] * num_vehicles,
        True,
        'Capacity'
    )

    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    params.time_limit.seconds = 3
    solution = routing.SolveWithParameters(params)

    if not solution:
        return None

    assignments = {}
    for vehicle_id in range(num_vehicles):
        index = routing.Start(vehicle_id)
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            if node_index != 0:
                customer_id = node_index - 1
                assignments[customer_id] = vehicle_id
            index = solution.Value(routing.NextVar(index))
    return assignments

if __name__ == "__main__":
    dataset = []
    for filename in sorted(os.listdir(INPUT_DIR)):
        if not filename.endswith(".json"): continue
        path = os.path.join(INPUT_DIR, filename)
        with open(path, "r") as f:
            data = json.load(f)
        try:
            # Use dynamic num_vehicles and capacity
            num_vehicles = data.get("num_vehicles", 3)
            capacity = data.get("vehicle_capacity", 15)
            assignments = solve_cvrp(data["customers"], data["demands"], num_vehicles, capacity)
            if assignments is None: continue
            features = [[c[0], c[1], d] for c, d in zip(data["customers"], data["demands"])]
            labels = [assignments.get(i, 0) for i in range(len(data["customers"]))]
            dataset.append({"features": features, "labels": labels})
        except Exception as e:
            print(f"Failed: {filename}, {e}")
            continue
    joblib.dump(dataset, OUTPUT_FILE)
    print(f"✅ Labels saved to {OUTPUT_FILE}")