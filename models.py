from dataclasses import dataclass
from typing import Tuple, List

# Классы необходимые для понятной работы алгоритма 

@dataclass
class Depot:
    id: int
    x: int
    y: int
    load_time: int

@dataclass
class Order:
    id: int
    x: int
    y: int
    volume: int
    time_window: Tuple[int, int]
    vehicle_service_time: int
    loader_cnt: int
    loader_service_time: int
    optional: bool

@dataclass
class Weights:
    order_penalty: int
    take_vehicle: int
    add_loader: int
    fuel_cost: int
    loader_work: int

@dataclass
class AnswerVehicles:
    id: int
    route: List[int]
    time: List[float]

@dataclass
class AnswerLoaders:
    id: int
    route: List[int]

@dataclass
class Scenario:
    vehicle_capacity: int
    vehicle_speed: int
    loader_speed: int
    vehicle_shift_size: int
    loader_shift_size: int
    depot: Depot
    weights: Weights
    orders: List[Order]
