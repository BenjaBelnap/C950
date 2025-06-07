#Benjamin Belnap Student ID:003177064

from entities.truck import Truck
from entities.package import Package
from hash import HashTable
import pandas as pd
import networkx as nx
from globals import State, speed, truck_capacity, delayed_packages, incorrect_address, startTime, preferred_truck, grouped_packages, backToHubTime


def load_truck(truck: Truck, package_table: HashTable, graph, current_time=startTime):
    """
    Load packages onto the truck using a greedy algorithm.
    Updates each package's loadTime.
    """
    simulate_time = pd.to_datetime(current_time, format='%H:%M:%S')
    truck.contents = []
    current_location = 'HUB'
    loaded_ids = set()

    while len(truck.contents) < truck_capacity:
        closest_package = None
        closest_distance = float('inf')
        # Find all available packages
        for package_id in range(1, package_table.capacity):
            node = package_table.search(package_id)
            if not node:
                continue
            package = node.value
            # Skip already loaded
            if package.status != State.AT_HUB or package_id in loaded_ids:
                continue
            # Delayed package logic
            if package_id in delayed_packages and current_time < pd.to_datetime('09:05:00', format='%H:%M:%S'):
                continue
            # Incorrect address logic
            destination = get_package_destination(package)
            if package_id in incorrect_address:
                if current_time < pd.to_datetime('10:20:00', format='%H:%M:%S'):
                    continue
                else:
                    destination = incorrect_address[package_id]
            # Preferred truck logic
            if package_id in preferred_truck and preferred_truck[package_id] != truck.key:
                continue
            # Grouped packages logic
            group = None
            for group_list in grouped_packages:
                if package_id in group_list:
                    group = group_list
                    break
            # if group:
            #     # Only load group if all are available and fit
            #     if any(package_table.search(pid).value.status != State.AT_HUB for pid in group):
            #         continue
            #     if len(truck.contents) + len(group) > truck_capacity:
            #         continue
            #     # Calculate distance for group
            #     group_dest = get_package_destination(package_table.search(group[0]).value)
            #     group_distance = distance_between(current_location, group_dest, graph)
            #     if group_distance is not None and group_distance < closest_distance:
            #         closest_package = group
            #         closest_distance = group_distance
            #     continue
            # Deadline priority
            if package.deadline:
                deadline_dt = pd.to_datetime(str(package.deadline), format='%H:%M:%S')
                if 0 < (deadline_dt - simulate_time).total_seconds() <= 4600:
                    closest_package = package
                    closest_distance = 0  # Force priority
                    needs_optimization = True
                    break
            # Greedy: closest distance
            distance = distance_between(current_location, destination, graph)
            if distance is None:
                raise ValueError(f"No distance found between {current_location} and {destination}. Check the graph data.")
            if distance is not None and distance < closest_distance:
                closest_distance = distance
                closest_package = package
            if package_id == 26:
                pass 

        if closest_package is None:
            break

        # Load package(s)
        if isinstance(closest_package, list):  # Grouped
            for pid in closest_package:
                pkg = package_table.search(pid).value
                pkg.status = State.IN_TRANSIT
                pkg.loadTime = simulate_time.time()
                truck.contents.append(pkg)
                loaded_ids.add(pid)
            current_location = get_package_destination(package_table.search(closest_package[0]).value)
        else:
            closest_package.status = State.IN_TRANSIT
            closest_package.loadTime = simulate_time.time()
            truck.contents.append(closest_package)
            loaded_ids.add(package_table.table.index(package_table.search(package_id)))
            current_location = get_package_destination(closest_package)
        #update simulation time
        travel_time = pd.Timedelta(hours=closest_distance / speed)
        simulate_time += travel_time

        #if this is the first load, make sure to be back right after backToHubTime
        print(f"Truck {truck.key} loading package {closest_package.package_id} at time {simulate_time.time()}.")
        if truck.mileage == 0 and truck.key == 1:
            print(simulate_time, backToHubTime)
            print(simulate_time  > backToHubTime)
            if simulate_time  > backToHubTime:
                break
    print(f"Truck {truck.key} loaded with {len(truck.contents)} packages at time {simulate_time.time()}.") 
            

def send_truck(truck: Truck, graph, current_time=startTime):
    """
    Simulates sending the truck on its route.
    Updates the truck's mileage, current location, and each package's deliveredAtTime.
    """
    simulate_time = pd.to_datetime(current_time, format='%H:%M:%S')
    total_distance = 0.0
    current_location = 'HUB'
    for package in truck.contents:
        destination = get_package_destination(package)
        distance = distance_between(current_location, destination, graph)
        if distance is None:
            distance = 0  # If no distance found, assume no travel
        if distance is not None:
            travel_time = pd.Timedelta(hours=distance / speed)
            simulate_time += travel_time
            package.deliveredAtTime = simulate_time.time()
            package.status = State.DELIVERED
            package.delivered_by_truck = truck.key  # Track which truck delivered the package
            total_distance += distance
            current_location = destination
    truck.mileage += total_distance
    truck.current_location = current_location

def all_delivered(package_table):
    response = True
    for i in range(1, package_table.capacity):
        node = package_table.search(i)
        if node and node.value.status != State.DELIVERED:
            response = False
        if node:
            print(node.value.status, node.value.package_id, node.value.address, node.value.city, node.value.zipCode, node.value.deliveredAtTime, node.value.deadline, node.value.weight)
    return response

def return_to_hub(truck, graph):
    if truck.current_location != 'HUB':
        distance = distance_between(truck.current_location, 'HUB', graph)
        if distance:
            truck.mileage += distance
            truck.current_location = 'HUB'

def validate_deliveries(package_table, grouped_packages, preferred_truck, delayed_packages):
    print("\nVALIDATION REPORT:")
    all_valid = True

    # Deadline validation
    for i in range(1, package_table.capacity):
        node = package_table.search(i)
        if node:
            pkg = node.value
            if pkg.deadline and pkg.deliveredAtTime and pkg.deliveredAtTime > pkg.deadline:
                print(f"Package {pkg.package_id} missed deadline! Delivered at {pkg.deliveredAtTime}, deadline was {pkg.deadline}")
                all_valid = False

    # Grouped packages validation
    for group in grouped_packages:
        loaded_times = set()
        for pid in group:
            node = package_table.search(pid)
            if node:
                loaded_times.add(node.value.loadTime)
        if len(loaded_times) > 1:
            print(f"Grouped packages {group} were not delivered together! Times: {loaded_times}")
            all_valid = False

    # Preferred truck validation
    for pid, truck_num in preferred_truck.items():
        node = package_table.search(pid)
        if node and hasattr(node.value, 'delivered_by_truck'):
            if node.value.delivered_by_truck != truck_num:
                print(f"Package {pid} was not delivered by preferred truck {truck_num}!")
                all_valid = False

    # Delayed arrival validation
    for pid in delayed_packages:
        node = package_table.search(pid)
        if node and node.value.loadTime and pd.to_datetime(str(node.value.loadTime)) < pd.to_datetime('09:05:00', format='%H:%M:%S'):
            print(f"Delayed package {pid} was loaded before 9:05 AM!")
            all_valid = False

    if all_valid:
        print("All validations passed!")


def distance_between(loc1, loc2, graph):
    """
    Returns the distance between two locations using the graph.
    If the edge does not exist, returns None.
    """
    if loc1 == loc2:
        return 0
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
        print(f"Processing location {i+1}/{len(locations)}: {loc1.strip()}")
        for j, loc2 in enumerate(locations):
            if i != j:  # Avoid self-loops
                distance = df.iloc[i + 1, j + 2]  # Distance values start from row 2, column 3
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
        
        #convert deadline to time object, none if EOD 
        if deadline == 'EOD':
            deadline = None
        else:
            deadline = pd.to_datetime(deadline, format='%H:%M:%S').time()

        weight = row['Weight\nKILO']
        status = State.AT_HUB  # Default status is AT_HUB
        delivered_at_time = None  # Default value

        package = Package(package_id,address, deadline, delivered_at_time, city, zip_code, weight, status)
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


    # load_truck(truck1, package_table, graph)
    # print(f"Truck 1 loaded with {len(truck1.contents)} packages.")
    # print("Truck 1 contents:")
    # for package in truck1.contents:
    #     print(f"Package ID: {package.package_id}, Status: {package.status.value}")
    # send_truck(truck1, graph)
    # print(f"Truck 1 sent to {truck1.current_location} with mileage: {truck1.mileage:.2f} miles.")

    trucks = [Truck(1, None), Truck(2, None)]
    truck_times = [startTime, startTime]

    # Add a field to Package for tracking which truck delivered it
    for i in range(1, package_table.capacity):
        node = package_table.search(i)
        if node:
            setattr(node.value, 'delivered_by_truck', None)
    #weight between hub and  5383 S 900 East #104\n(84117)
    print(f"Distance from HUB to 5383 S 900 East #104: {distance_between('HUB', '5383 S 900 East #104\n(84117)', graph)} miles")
    #debug package 23
    print(package_table.search(26).value.address, package_table.search(26).value.city, package_table.search(26).value.zipCode)
    print(f"Distance from HUB to package 26: {distance_between('HUB', get_package_destination(package_table.search(26).value), graph)} miles")
    print(f"Distance from HUB to package 25: {distance_between('HUB', get_package_destination(package_table.search(25).value), graph)} miles")
    print(get_package_destination(package_table.search(26).value))
    print(get_package_destination(package_table.search(25).value))
    count = 0
    while not all_delivered(package_table):
        for idx, truck in enumerate(trucks):
            load_truck(truck, package_table, graph, truck_times[idx])
            # Mark which truck delivers each package
            if truck.contents:
                print(f"Truck {truck.key} loaded with {len(truck.contents)} packages.")
                send_truck(truck, graph, truck_times[idx])
                # Advance truck's time to last delivery
                if truck.contents:
                    last_delivery_time = max([pkg.deliveredAtTime for pkg in truck.contents if pkg.deliveredAtTime])
                    truck_times[idx] = pd.to_datetime(str(last_delivery_time))
            else:
                # If nothing loaded, advance time to next available package (e.g., delayed)
                truck_times[idx] += pd.Timedelta(minutes=5)
            truck.contents = []  # Clear truck contents after delivery
            return_to_hub(truck, graph)
        count += 1
        print(f"\nIteration {count}:")

    print(f"\nAll packages delivered!")
    for idx, truck in enumerate(trucks):
        print(f"Truck {truck.key} total mileage: {truck.mileage:.2f}")

    validate_deliveries(package_table, grouped_packages, preferred_truck, delayed_packages)
    #package 6 loaded at time
    print(f"Package 6 load time: {package_table.search(6).value.loadTime} package 6 delivered by truck: {package_table.search(6).value.delivered_by_truck}")



    
    