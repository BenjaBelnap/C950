class Package:
    def __init__(self, address, deadline, deliveredAtTime, city, zipCode, weight, status):
        self.address = address
        self.deadline = deadline
        self.deliveredAtTime = deliveredAtTime
        self.city = city
        self.zipCode = zipCode
        self.weight = weight
        self.status = status
        self.loadTime = None

        

