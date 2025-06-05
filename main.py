from entities.truck import Truck
from entities.package import Package
from hash import HashTable
import pandas as pd
import networkx as nx

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
    cleaned_locations = []




    graph = nx.Graph()  # Create a bidirectional graph

    # Add edges to the graph
    for i, loc1 in enumerate(locations):
        for j, loc2 in enumerate(locations):
            if i != j:  # Avoid self-loops
                distance = df.iloc[i + 1, j + 2]  # Distance values start from row 2, column 2
                if not pd.isna(distance):  # Skip NaN values
                    graph.add_edge(loc1.strip(), loc2.strip(), weight=distance)

    # Example: Print edges with weights
    for edge in graph.edges(data=True):
        print(edge)

    #sanity checks
    edge_data = graph.get_edge_data('1060 Dalton Ave S\n(84104)', 'HUB')
    print(edge_data['weight'])  # Should print the distance between HUB and 1060 Dalton Ave S (84104)


    # Load the package Excel file
    package_file = "WGUPS Package File.xlsx"  # Update if your filename is different
    df = pd.read_excel(package_file, header=7)  # Data starts at row 9 (header=8, 0-indexed)

    package_table = HashTable(capacity=41) 

    # Iterate through the DataFrame and insert packages
    for _, row in df.iterrows():
        package_id = int(row['Package\nID'])
        address = row['Address']
        city = row['City ']
        zip_code = str(row['Zip'])
        deadline = row['Delivery\nDeadline']
        weight = row['Weight\nKILO']
        status = "At Hub"  # Default status
        delivered_at_time = None  # Default value

        package = Package(address, deadline, delivered_at_time, city, zip_code, weight, status)
        package_table.insert(package_id, package)
        
    ex_package = package_table.search(1)  # Example to search for package with ID 1
    if ex_package:
        print(f"Package ID 1: {ex_package.value.address}, {ex_package.value.city}, {ex_package.value.zipCode}")
    else:
        print("Package not found.")
    package_destination = get_package_destination(ex_package.value)  # Get destination of the example package
    print(package_destination)  # Example package destination
    print(distance_between(package_destination, 'HUB', graph))  # Example distance check

    
    