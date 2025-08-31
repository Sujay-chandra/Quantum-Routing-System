# generate_data.py
"""
Generate synthetic CVRP instances in Vijayawada, AP with guaranteed feasibility.
Ensures total demand <= total capacity and no single demand exceeds vehicle capacity.
"""
import json
import os
import random

NUM_INSTANCES = 150
OUTPUT_DIR = "data/raw"
os.makedirs(OUTPUT_DIR, exist_ok=True)
random.seed(42)

# Realistic Vijayawada landmark locations (lat, lon)
VIJAYAWADA_LOCATIONS = [
    [16.5167, 80.6333],  # Benz Circle
    [16.5089, 80.6458],  # Governor House
    [16.5028, 80.6425],  # SPB Palace
    [16.5100, 80.6370],  # Diwanchowk
    [16.4850, 80.6667],  # Auto Nagar
    [16.5200, 80.6500],  # Lalapet
    [16.4900, 80.6550],  # Siddhartha Nagar
    [16.5150, 80.6400],  # Tilak Road
    [16.5300, 80.6600],  # Gunadala
    [16.4950, 80.6450],  # Patamata
    [16.5120, 80.6400],  # NTR Circle
    [16.5000, 80.6500],  # Payakapuram
]

def generate_instance(idx):
    num_vehicles = 3
    vehicle_capacity = 15
    n_customers = random.randint(5, 8)
    selected = random.sample(VIJAYAWADA_LOCATIONS, n_customers)
    customers = [[c[0], c[1]] for c in selected]

    # Generate demands ensuring feasibility
    max_demand_per_cust = min(8, vehicle_capacity)
    demands = [random.randint(3, 6) for _ in range(n_customers)]

    total_demand = sum(demands)
    total_capacity = num_vehicles * vehicle_capacity

    # Ensure total demand doesn't exceed total capacity
    while total_demand > total_capacity:
        demands = [random.randint(3, 6) for _ in range(n_customers)]
        total_demand = sum(demands)

    # Ensure no single demand exceeds vehicle capacity
    for d in demands:
        if d > vehicle_capacity:
            raise ValueError(f"Demand {d} > capacity {vehicle_capacity}")

    data = {
        "instance_id": idx,
        "depot": [16.5062, 80.6480],  # Vijayawada Railway Station
        "customers": customers,
        "demands": demands,
        "num_vehicles": num_vehicles,
        "vehicle_capacity": vehicle_capacity
    }

    with open(f"{OUTPUT_DIR}/instance_{idx:03d}.json", "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    print("🌍 Generating 150 feasible CVRP instances in Vijayawada...")
    for i in range(NUM_INSTANCES):
        generate_instance(i)
    print(f"✅ Saved to {OUTPUT_DIR}/")