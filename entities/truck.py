class Truck:
    def __init__(self, key: int, contents: list[int], mileage: float = 0.0):
        self.key = key
        self.contents = contents
        self.mileage = mileage
        self.current_location = 'HUB'
