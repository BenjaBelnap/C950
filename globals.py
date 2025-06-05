from enum import Enum
class State(Enum):
    """
    Enum to represent the state of a package.
    """
    AT_HUB = "At Hub"
    IN_TRANSIT = "In Transit"
    DELIVERED = "Delivered"