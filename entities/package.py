class Package:
    def __init__(self,package_id, address, deadline, deliveredAtTime, city, zipCode, weight, status):
        self.package_id = package_id
        self.address = address
        self.deadline = deadline
        self.deliveredAtTime = deliveredAtTime
        self.city = city
        self.zipCode = zipCode
        self.weight = weight
        self.status = status
        self.loadTime = None
        self.deliveredByTruck = None

        

