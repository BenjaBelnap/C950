import hash
import entities.truck as truck
import entities.package as package
import pandas as pd
import networkx as nx

if __name__ == "__main__":
    # Load the Excel file
    file_path = "WGUPS Distance Table.xlsx"  # Replace with your file path
    df = pd.read_excel(file_path, header=None)

    # Parse the data
    locations = df.iloc[1:, 1].tolist()  # Extract location names (column A, skipping the header)
    cleaned_locations = []

    for location in locations:
        if isinstance(location, str):  # Ensure the value is a string
            address = location.split('\n')[-1].strip()  # Take the last line (address) and strip whitespace
            cleaned_locations.append(address)


    graph = nx.Graph()  # Create a bidirectional graph

    # Add edges to the graph
    for i, loc1 in enumerate(locations):
        for j, loc2 in enumerate(locations):
            if i != j:  # Avoid self-loops
                distance = df.iloc[i + 1, j + 2]  # Distance values start from row 2, column 2
                if not pd.isna(distance):  # Skip NaN values
                    graph.add_edge(loc1, loc2, weight=distance)

    # Example: Print edges with weights
    for edge in graph.edges(data=True):
        print(edge)

    #sanity checks
    edge_data = graph.get_edge_data(' 1060 Dalton Ave S\n(84104)', ' HUB')
    print(edge_data['weight'])  # Should print the distance between HUB and 1060 Dalton Ave S (84104)

    
    