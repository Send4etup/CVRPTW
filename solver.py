import math
import json
from pyvrp import Model
from pyvrp.stop import MaxRuntime

from models import Scenario

SCALE = 100  # multiply all distances/times to work with integers


def _dist(x1, y1, x2, y2) -> float:
    return round(math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2), 2)


def _compute_times(order_ids: list, scenario: Scenario) -> list:
    """Service start time at each order stop (unscaled, real units)."""
    by_id = {o.id: o for o in scenario.orders}
    speed = scenario.vehicle_speed
    t = 0.0
    px, py = scenario.depot.x, scenario.depot.y
    times = []
    for oid in order_ids:
        o = by_id[oid]
        t += _dist(px, py, o.x, o.y) / speed
        t = max(t, o.time_window[0])
        times.append(round(t, 2))
        t += o.vehicle_service_time
        px, py = o.x, o.y
    return times


def solve(scenario: Scenario) -> dict:
    m = Model()

    coords = [(scenario.depot.x, scenario.depot.y)] + [(o.x, o.y) for o in scenario.orders]

    depot_node = m.add_depot(
        x=scenario.depot.x,
        y=scenario.depot.y,
        tw_early=0,
        tw_late=scenario.vehicle_shift_size * SCALE,
    )

    client_nodes = []
    for order in scenario.orders:
        c = m.add_client(
            x=order.x,
            y=order.y,
            delivery=order.volume,
            service_duration=order.vehicle_service_time * SCALE,
            tw_early=order.time_window[0] * SCALE,
            tw_late=order.time_window[1] * SCALE,
            prize=scenario.weights.order_penalty * SCALE if order.optional else 0,
            required=not bool(order.optional),
        )
        client_nodes.append(c)

    all_nodes = [depot_node] + client_nodes
    for i, (ni, (xi, yi)) in enumerate(zip(all_nodes, coords)):
        for j, (nj, (xj, yj)) in enumerate(zip(all_nodes, coords)):
            if i != j:
                d = _dist(xi, yi, xj, yj)
                m.add_edge(
                    ni, nj,
                    distance=round(d * SCALE),
                    duration=round(d / scenario.vehicle_speed * SCALE),
                )

    m.add_vehicle_type(
        num_available=len(scenario.orders),
        capacity=scenario.vehicle_capacity,
        shift_duration=scenario.vehicle_shift_size * SCALE,
        fixed_cost=scenario.weights.take_vehicle * SCALE,
        unit_distance_cost=scenario.weights.fuel_cost,
    )

    result = m.solve(stop=MaxRuntime(10), display=False)

    vehicles = []
    for vid, route in enumerate(result.best.routes(), start=1):
        # visits() returns location indices: depot=0, clients=1..n
        order_ids = [scenario.orders[i - 1].id for i in route.visits()]
        times = _compute_times(order_ids, scenario)
        vehicles.append({
            "id": vid,
            "route": [0] + order_ids + [0],
            "time": times,
        })

    return {"vehicles": vehicles, "loaders": []}
