class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value

class HashTable:
    def __init__(self, capacity):
        self.capacity = capacity
        self.table = [None] * capacity
        self.size = 0

    def hash(self, key):
        return(key)
    
    def insert(self, key, value):
        index = self.hash(key)

        if self.table[index]:
            raise(KeyError)
        else:
            self.table[index] = Node(key,value)
    
    def search(self, key):
        index = self.hash(key)
        return(self.table[index])
    
    

