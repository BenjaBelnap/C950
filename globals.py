from enum import Enum
import pandas as pd
class State(Enum):
    """
    Enum to represent the state of a package.
    """
    AT_HUB = "At Hub"
    IN_TRANSIT = "In Transit"
    DELIVERED = "Delivered"

speed = 18  # Speed of the trucks in miles per hour
truck_capacity = 16  # Maximum number of packages a truck can carry
delayed_packages = [6,25,28,32]  # List to hold packages that are delayed - 9:05 AM
incorrect_address = {
    9: "410 S State St\n(84111)"
}
startTime = pd.to_datetime('08:00:00', format='%H:%M:%S')  # Start time of the simulation
preferred_truck = {
    3: 2,
    18: 2,
    36: 2,
    38: 2
}
grouped_packages = [
    [15,13,19]
]