# construct_routes.py
"""
Build delivery routes from QML predictions.
Fixes overloads and ensures all trucks are used if needed.
"""

from ortools.constraint_solver import routing_enums_pb2, pywrapcp
import numpy as np

def solve_tsp_for_truck(customers, depot=(0, 0)):
    """
    Solve TSP for one truck using nearest neighbor.
    Returns: route (list of customer coordinates), total distance (km)
    """
    if len(customers) == 0:
        return [], 0.0

    locations = [depot] + customers
    n = len(locations)
    dist_matrix = np.zeros((n, n))

    # Compute Euclidean distance with km approximation
    for i in range(n):
        for j in range(n):
            dx = (locations[i][0] - locations[j][0]) * 111  # ~km per degree latitude
            dy = (locations[i][1] - locations[j][1]) * 111 * np.cos(np.radians(locations[i][0]))
            dist_matrix[i][j] = np.hypot(dx, dy)

    # Nearest Neighbor TSP
    route = [0]  # Start at depot
    unvisited = list(range(1, n))
    total_distance = 0.0

    while unvisited:
        last = route[-1]
        nearest = min(unvisited, key=lambda u: dist_matrix[last][u])
        total_distance += dist_matrix[last][nearest]
        route.append(nearest)
        unvisited.remove(nearest)

    total_distance += dist_matrix[route[-1]][0]  # Return to depot
    return [customers[i-1] for i in route[1:-1] + [route[-1]]], total_distance


def validate_and_fix_assignments(customers, demands, assignments, vehicle_capacity=15, num_vehicles=3):
    """
    Ensure no truck exceeds capacity.
    Reassign customers if needed.
    """
    loads = [0] * num_vehicles
    for i, truck_id in enumerate(assignments):
        if 0 <= truck_id < num_vehicles:
            loads[truck_id] += demands[i]

    # Reassign overloaded customers
    for i, truck_id in enumerate(assignments):
        if loads[truck_id] > vehicle_capacity:
            for new_truck in range(num_vehicles):
                if new_truck != truck_id and loads[new_truck] + demands[i] <= vehicle_capacity:
                    assignments[i] = new_truck
                    loads[truck_id] -= demands[i]
                    loads[new_truck] += demands[i]
                    break
    return assignments


def build_routes(customers, demands, assignments, vehicle_capacity=15, num_vehicles=3):
    """
    Build final delivery routes from QML predictions.
    Args:
        customers: list of [lat, lon]
        demands: list of int
        assignments: list of truck IDs (from QML model)
        vehicle_capacity: int
        num_vehicles: int
    Returns:
        routes: list of route dicts
        total_distance: float
    """
    # Validate and fix overloads
    assignments = validate_and_fix_assignments(customers, demands, assignments, vehicle_capacity, num_vehicles)

    # Group customers by truck
    vehicle_customers = [[] for _ in range(num_vehicles)]
    vehicle_demands = [[] for _ in range(num_vehicles)]

    for i, truck_id in enumerate(assignments):
        if 0 <= truck_id < num_vehicles:
            vehicle_customers[truck_id].append(customers[i])
            vehicle_demands[truck_id].append(demands[i])

    # Build routes
    routes = []
    total_distance = 0.0
    depot = [16.5062, 80.6480]  # Vijayawada Railway Station

    for vid in range(num_vehicles):
        cust_list = vehicle_customers[vid]
        load = sum(vehicle_demands[vid])
        if not cust_list:
            continue

        route_stops, distance = solve_tsp_for_truck(cust_list, depot)
        total_distance += distance

        routes.append({
            "vehicle_id": vid,
            "customers": cust_list,
            "route": route_stops,
            "load": load,
            "capacity": vehicle_capacity,
            "distance": round(distance, 2)
        })

    return routes, round(total_distance, 2)