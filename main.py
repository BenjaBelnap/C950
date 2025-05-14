import hash
import entities.truck as truck
import entities.package as package

if __name__ == "__main__":
    myHash = hash.HashTable(10)
    for i in range(10):
        myHash.insert(i,package.Package(None,None,None,None,None,"delivered"))
    
    print(myHash.table)
    for object in myHash.table:
        print(object.value.status)