import json

from models import Scenario, Depot, Weights, Order
from solver import solve


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


if __name__ == "__main__":
    scenario = parse("data/input.json")
    result = solve(scenario)
    print(json.dumps(result, indent=2))