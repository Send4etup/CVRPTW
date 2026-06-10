import json
import math
from pyvrp import Model
from pyvrp.stop import MaxRuntime

from models import Scenario, Depot, Weights, Order


def parse(path: str) -> Scenario:
    with open(path) as f:
        raw = json.load(f)

    depot = Depot(**raw["depot"])
    weights = Weights(**raw["weights"])
    orders = [Order(**o) for o in raw["orders"]]

    return Scenario(
        depot=depot,
        weights=weights,
        orders=orders,
        vehicle_capacity=raw["vehicle_capacity"],
        vehicle_speed=raw["vehicle_speed"],
        loader_speed=raw["loader_speed"],
        vehicle_shift_size=raw["vehicle_shift_size"],
        loader_shift_size=raw["loader_shift_size"],
    )


def find_distance(x1, y1, x2, y2) -> float:
    return round(math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2), 2)


def compute_times(order_ids: list, scenario: Scenario) -> list:
    by_id = {order.id: order for order in scenario.orders}

    time = 0.0
    times = []
    px, py = scenario.depot.x, scenario.depot.y

    for order_id in order_ids:
        order = by_id[order_id]

        time += find_distance(px, py, order.x, order.y) / scenario.vehicle_speed
        time = max(time, order.time_window[0])
        times.append(round(time, 2))
        time += order.vehicle_service_time
        px, py = order.x, order.y

    return times


def fill_model(scenario, model):
    coordinates = [(scenario.depot.x, scenario.depot.y)] + [(order.x, order.y) for order in scenario.orders]

    depot = model.add_depot(x=scenario.depot.x, y=scenario.depot.y, tw_early=0, tw_late=scenario.vehicle_shift_size)

    clients = []

    for order in scenario.orders:
        c = model.add_client(x=order.x, y=order.y, delivery=order.volume, service_duration=order.vehicle_service_time,
                             tw_early=order.time_window[0], tw_late=order.time_window[1],
                             prize=scenario.weights.order_penalty if order.optional else 0,
                             required=not bool(order.optional))

        clients.append(c)

    all_nodes = [depot] + clients

    for i, (node_i, (x_i, y_i)) in enumerate(zip(all_nodes, coordinates)):
        for j, (node_j, (x_j, y_j)) in enumerate(zip(all_nodes, coordinates)):
            if i != j:
                distance = find_distance(x_i, y_i, x_j, y_j)

                model.add_edge(node_i, node_j, distance=round(distance),
                               duration=round(distance / scenario.vehicle_speed))

    model.add_vehicle_type(num_available=len(scenario.orders), capacity=scenario.vehicle_capacity,
                           shift_duration=scenario.vehicle_shift_size, fixed_cost=scenario.weights.take_vehicle,
                           unit_distance_cost=scenario.weights.fuel_cost)


def calculate_vehicles_routes(result):
    vehicles = []

    for vehicle_id, route in enumerate(result.best.routes(), start=1):
        order_ids = [scenario.orders[i - 1].id for i in route.visits()]
        times = compute_times(order_ids, scenario)

        vehicles.append({
            "id": vehicle_id,
            "route": [0] + order_ids + [0],
            "time": times,
        })

    return vehicles


if __name__ == "__main__":
    scenario = parse("data/input.json")

    model = Model()

    fill_model(scenario, model)

    result = model.solve(stop=MaxRuntime(10))

    vehicles = calculate_vehicles_routes(result)

    print(vehicles)
