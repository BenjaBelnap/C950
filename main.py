#Benjamin Belnap Student ID:003177064

from entities.truck import Truck
from entities.package import Package
from hash import HashTable
import pandas as pd
import networkx as nx
from globals import State, speed, truck_capacity, delayed_packages, incorrect_address, startTime


#greedy algorithm to load trucks
def load_truck(truck:Truck, package_table:HashTable, graph, current_time=startTime):
    """
    Load packages onto the truck using a greedy algorithm.
    """
    simulate_time = pd.to_datetime(current_time, format='%H:%M:%S')
    truck.contents = []
    current_location = 'HUB'
    while len(truck.contents) < truck_capacity:  
        closest_package = None
        closest_distance = float('inf')
        for package_id in range(package_table.capacity - 1):
            package = package_table.search(package_id + 1).value
            if package.status == State.AT_HUB:
                destination = get_package_destination(package)
                distance = distance_between(current_location, destination, graph)
                if distance is None and current_location == get_package_destination(package):
                    distance = 0.0  # If the package is at the current location, distance is 0
                # Check if the package is delayed or has an incorrect address
                if package_id + 1 in delayed_packages:
                    if current_time < pd.to_datetime('09:05:00', format='%H:%M:%S'):
                        continue  # Skip loading delayed packages before 9:05 AM
                if package_id + 1 in incorrect_address:
                    if current_time < pd.to_datetime('10:20:00', format='%H:%M:%S'):
                        continue # Skip loading packages with incorrect address before 10:20 AM
                    else:
                        destination = incorrect_address[package_id + 1]
                if distance is not None and distance < closest_distance:
                    closest_distance = distance
                    closest_package = package
        
        if closest_package is None:  # No more packages to load
            break
        
        # Load the closest package onto the truck
        truck.contents.append(closest_package)
        closest_package.status = State.IN_TRANSIT
        current_location = get_package_destination(closest_package)

def send_truck(truck: Truck, graph,current_time=startTime):
    """
    Simulates sending the truck on its route.
    Updates the truck's mileage and current location.
    """
    total_distance = 0.0
    current_location = 'HUB'
    
    for package in truck.contents:
        destination = get_package_destination(package)
        distance = distance_between(current_location, destination, graph)
        
        if distance is not None:
            total_distance += distance
            current_location = destination
    
    # Update truck's mileage and current location
    truck.mileage += total_distance
    truck.current_location = current_location


def distance_between(loc1, loc2, graph):
    """
    Returns the distance between two locations using the graph.
    If the edge does not exist, returns None.
    """
    if graph.has_edge(loc1, loc2):
        return graph[loc1][loc2]['weight']
    return None

def get_package_destination(package):
    """
    Returns the destination of a package in the format 'Address (Zip Code)'.
    """
    return f"{package.address}\n({package.zipCode})"

if __name__ == "__main__":
    # Load the Excel file
    file_path = "WGUPS Distance Table.xlsx" 
    df = pd.read_excel(file_path, header=None)

    # Parse the data
    locations = df.iloc[1:, 1].tolist()  # Extract location names (column A, skipping the header)




    graph = nx.Graph()  # Create a bidirectional graph

    # Add edges to the graph
    for i, loc1 in enumerate(locations):
        for j, loc2 in enumerate(locations):
            if i != j:  # Avoid self-loops
                distance = df.iloc[i + 1, j + 2]  # Distance values start from row 2, column 2
                if not pd.isna(distance):  # Skip NaN values
                    graph.add_edge(loc1.strip(), loc2.strip(), weight=distance)

    # Example: Print edges with weights
    # for edge in graph.edges(data=True):
    #     print(edge)

    #sanity checks
    # edge_data = graph.get_edge_data('1060 Dalton Ave S\n(84104)', 'HUB')
    # print(edge_data['weight'])  # Should print the distance between HUB and 1060 Dalton Ave S (84104)


    # Load the package Excel file
    package_file = "WGUPS Package File.xlsx"  # Update if your filename is different
    df = pd.read_excel(package_file, header=7)  # Data starts at row 9 (header=8, 0-indexed)

    package_table = HashTable(capacity=41) 

    # Iterate through the DataFrame and insert packages
    for _, row in df.iterrows():
        package_id = int(row['Package\nID'])
        address = row['Address']
        city = row['City ']
        zip_code = row['Zip']
        deadline = row['Delivery\nDeadline']
        
        #convert deadline to time object, none if EOD e.g. 10:30:00
        if deadline == 'EOD':
            deadline = None
        else:
            deadline = pd.to_datetime(deadline, format='%H:%M:%S').time()

        weight = row['Weight\nKILO']
        status = State.AT_HUB  # Default status is AT_HUB
        delivered_at_time = None  # Default value

        package = Package(address, deadline, delivered_at_time, city, zip_code, weight, status)
        package_table.insert(package_id, package)
        
    # ex_package = package_table.search(1)  # Example to search for package with ID 1
    # if ex_package:
    #     print(f"Package ID 1: {ex_package.value.address}, {ex_package.value.city}, {ex_package.value.zipCode}", 
    #           f"Status: {ex_package.value.status.value}, Deadline: {ex_package.value.deadline}",
    #           f"Weight: {ex_package.value.weight} KILO")
    # else:
    #     print("Package not found.")
    # package_destination = get_package_destination(ex_package.value)  # Get destination of the example package
    # print(package_destination)  # Example package destination
    # print(distance_between(package_destination, 'HUB', graph))  # Example distance check

    truck1 = Truck(1,  None)
    truck2 = Truck(2,  None)

    load_truck(truck1, package_table, graph)
    print(f"Truck 1 loaded with {len(truck1.contents)} packages.")
    print("Truck 1 contents:")
    for package in truck1.contents:
        print(f"Package ID: {package.address}, Status: {package.status.value}")
    send_truck(truck1, graph)
    print(f"Truck 1 sent to {truck1.current_location} with mileage: {truck1.mileage:.2f} miles.")



    
    