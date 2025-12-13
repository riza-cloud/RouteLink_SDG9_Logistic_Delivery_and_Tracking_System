from collections import deque

# Dynamic array for storing delivery records
# Each delivery = {id, sender, receiver, destination, status}
deliveries = []

# Queue for scheduling
schedule_queue = deque()

# Completed deliveries with route info
completed_deliveries = []

# Graph for mapping delivery routes
routes = {
    "Warehouse": ["Area A", "Area B"],
    "Area A": ["Area C", "Area D"],
    "Area B": ["Area E", "Area F"],
    "Area C": [],
    "Area D": [],
    "Area E": [],
    "Area F": []
}

# Travel time between areas (in minutes)
travel_times = {
    ("Warehouse", "Area A"): 3,
    ("Warehouse", "Area B"): 4,
    ("Area A", "Area C"): 3,
    ("Area A", "Area D"): 3,
    ("Area B", "Area E"): 4,
    ("Area B", "Area F"): 4
}

# Status options
status_options = {
    "1": "Pending",
    "2": "Dispatched",
    "3": "Out for Delivery",
    "4": "Delivered"
}


# SORTING ALGORITHMS

def quick_sort(arr, key):
    if len(arr) <= 1:
        return arr
     
   # Use the first element as a simple pivot for simplicity in this context
    pivot = arr[0] 
    pivot_val = pivot.get(key)
    
    # Handle the case where the key might not exist (though unlikely in this schema)
    if pivot_val is None:
        return arr
        
    left = [x for x in arr if x.get(key) < pivot_val]
    middle = [x for x in arr if x.get(key) == pivot_val]
    right = [x for x in arr if x.get(key) > pivot_val]
    
    return quick_sort(left, key) + middle + quick_sort(right, key)

def group_sort(arr, primary_key, secondary_key):
    """Sorts deliveries first by primary key, then by secondary key (Group Sort)"""
    groups = {}
    for item in arr:
        key = item.get(primary_key)
        if key not in groups:
            groups[key] = []
        groups[key].append(item)
        
    final_sorted_list = []
    
    # The order of the status_options dictionary values is used for a logical sequence
    status_order = {status: i for i, status in enumerate(status_options.values())}
    
    # Sort the groups by the defined order of the primary key (Status)
    sorted_groups_keys = sorted(groups.keys(), key=lambda k: status_order.get(k, 99))
    
    # Sort each group by the secondary key (Destination) and combine
    for key in sorted_groups_keys:
        
     # Sort each group (already filtered by status) by the secondary key (Destination)
        sorted_group = quick_sort(groups[key], secondary_key)
        final_sorted_list.extend(sorted_group)
        
    return final_sorted_list

# HELPER FUNCTIONS

def find_route(destination):
    """BFS to find route from Warehouse to destination"""
    queue = deque([("Warehouse", ["Warehouse"])])
    visited = set()
    
    while queue:
        current, path = queue.popleft()
        
        if current == destination:
            return path
        
        if current in visited:
            continue
        
        visited.add(current)
        
        
        for child in routes.get(current, []):
            if child not in visited:
                queue.append((child, path + [child]))

    return []


def calculate_travel_time(route):
    """Calculate total travel time for a route"""
    total_time = 0
    for i in range(len(route) - 1):
        edge = (route[i], route[i+1])
        total_time += travel_times.get(edge, 0)
    return total_time

def get_active_delivery():
    """Get the currently active (non-pending, non-delivered) delivery"""
    for d in deliveries:
        if d["status"] in ["Dispatched", "Out for Delivery"]:
            return d
    return None


# CORE FUNCTIONS

def register_delivery():
    print("\n--- Register Delivery ---")
    parcel_id = input("Enter Parcel ID: ")
    sender = input("Enter Sender Name: ")
    receiver = input("Enter Receiver Name: ")
    destination = input("Enter Destination Location: ")

    # Check if there's already an active delivery
    active_delivery = get_active_delivery()
    
    if active_delivery is None:
        # No active delivery, so this one gets dispatched immediately
        status = "Dispatched"
        print(f"No active delivery found. Parcel {parcel_id} is now DISPATCHED!")
    else:
        # There's an active delivery, so this one goes to pending
        status = "Pending"
        print(f"Delivery in progress (ID: {active_delivery['id']}). Parcel {parcel_id} added to queue as PENDING.")

    record = {
        "id": parcel_id,
        "sender": sender,
        "receiver": receiver,
        "destination": destination,
        "status": status
    }

    deliveries.append(record)
    schedule_queue.append(record)
    print("Delivery Registered & Added to Queue!")

def update_status():
    print("\n--- Update Delivery Status ---")
    
    # Show only active or pending deliveries
    active_deliveries = [d for d in deliveries if d["status"] != "Delivered"]
    
    if not active_deliveries:
        print("No active deliveries to update.")
        return
    
    print("\nActive Deliveries:")
    for d in active_deliveries:
        print(f"ID: {d['id']} - Status: {d['status']}")
    
    parcel_id = input("\nEnter Parcel ID to update: ")

    for d in deliveries:
        if d["id"] == parcel_id:
            print(f"Current Status: {d['status']}")
            print("\nSelect New Status:")
            print("[1] Pending")
            print("[2] Dispatched")
            print("[3] Out for Delivery")
            print("[4] Delivered")
            
            choice = input("Enter choice (1-4): ")
            
            if choice in status_options:
                old_status = d["status"]
                new_status = status_options[choice]
                d["status"] = new_status
                print(f"Status Updated to: {new_status}!")
                
                # If this delivery was completed, record it with route info
                if new_status == "Delivered" and old_status in ["Dispatched", "Out for Delivery"]:
                    route = find_route(d["destination"])
                    route_str = " -> ".join(route) if route else "N/A"
                    travel_time = calculate_travel_time(route) if route else 0
                    
                    completed_record = {
                        "id": d["id"],
                        "sender": d["sender"],
                        "receiver": d["receiver"],
                        "origin": "Warehouse",
                        "destination": d["destination"],
                        "route": route_str,
                        "time": travel_time,
                        "status": "Delivered"
                    }
                    completed_deliveries.append(completed_record)
                    
                    show_status_report()
                    dispatch_next_pending()
            else:
                print("Invalid choice. Status not updated.")
            return

    print("Parcel ID not found.")

def dispatch_next_pending():
    """Automatically dispatch the next pending delivery in queue"""
    for d in schedule_queue:
        if d["status"] == "Pending":
            d["status"] = "Dispatched"
            print(f"\n>>> Next delivery auto-dispatched: ID {d['id']} to {d['destination']}")
            return
    print("\n>>> No pending deliveries in queue.")

def show_status_report():
    """Display all delivered items in table format"""
    delivered = [d for d in deliveries if d["status"] == "Delivered"]
    
    if not delivered:
        print("\nNo deliveries completed today.")
        return
    
    print("\n--- Status Report: Delivered Today ---")
    print("-" * 85)
    print(f"{'ID':<10} {'Sender':<15} {'Receiver':<15} {'Destination':<15} {'Status':<10}")
    print("-" * 85)
    
    for d in delivered:
        print(f"{d['id']:<10} {d['sender']:<15} {d['receiver']:<15} {d['destination']:<15} {d['status']:<10}")
    
    print("-" * 85)

def view_status_report():
    """View deliveries filtered by status with sorting"""
    while True:
        print("\n--- Status Report Viewing ---")
        print("Filter by Status:")
        print("[1] Pending")
        print("[2] Dispatched")
        print("[3] Out for Delivery")
        print("[4] Delivered")
        print("[0] Show All / Reset")
        print("[9] Back to Main Menu")
        
        choice = input("Enter choice: ")
        
        if choice == "9":
            break
        
        if choice == "0":
            # Show all deliveries sorted by destination
            filtered = deliveries
            filter_name = "All Deliveries"
        elif choice in status_options:
            # Filter by selected status
            status = status_options[choice]
            filtered = [d for d in deliveries if d["status"] == status]
            filter_name = f"{status} Deliveries"
        else:
            print("Invalid choice. Try again.")
            continue
        
        if not filtered:
            print(f"\nNo {filter_name.lower()} found.")
            continue
        
        # Sort by destination using quick sort
        sorted_deliveries = quick_sort(filtered, key="destination")
        
        print(f"\n--- {filter_name} (Sorted by Destination) ---")
        print("-" * 95)
        print(f"{'ID':<10} {'Sender':<15} {'Receiver':<15} {'Destination':<15} {'Status':<15}")
        print("-" * 95)
        
        for d in sorted_deliveries:
            print(f"{d['id']:<10} {d['sender']:<15} {d['receiver']:<15} {d['destination']:<15} {d['status']:<15}")
        
        print("-" * 95)
        print(f"Total: {len(sorted_deliveries)} deliveries")

def sort_deliveries():
    print("\n--- Sort Deliveries by Destination ---")
    sorted_list = quick_sort(deliveries, key="destination")

    for d in sorted_list:
        print(f"{d['id']} - {d['destination']} - {d['status']}")

def show_map():
    print("\n--- Route Map (Graph) ---")
    for place, connected in routes.items():
        print(f"{place} -> {', '.join(connected) if connected else 'No outgoing routes'}")
    
    # Show completed deliveries with route summary
    if not completed_deliveries:
        print("\n--- Route Summary Table ---")
        print("No completed deliveries yet.")
        return
    
    print("\n--- Route Summary Table (Completed Deliveries Only) ---")
    print("-" * 90)
    print(f"{'ID':<10} {'Origin':<15} {'Destination':<15} {'Route':<30} {'Time (min)':<10}")
    print("-" * 90)
    
    for delivery in completed_deliveries:
        print(f"{delivery['id']:<10} {delivery['origin']:<15} {delivery['destination']:<15} {delivery['route']:<30} {delivery['time']:<10}")
    
    print("-" * 90)

# MAIN MENU

def main_menu():
    while True:
        print("\n==============================")
        print(" LOGISTIC DELIVERY SYSTEM ")
        print("==============================")
        print("1. Register Delivery")
        print("2. Update Delivery Status **(Free Update)**")
        print("3. View Status Report **(Group Sort)**")
        print("4. Quick Sort Deliveries")
        print("5. Show Route Map (Graph)")
        print("6. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            register_delivery()
        elif choice == "2":
            update_status()
        elif choice == "3":
            view_status_report()
        elif choice == "4":
            sort_deliveries()
        elif choice == "5":
            show_map()
        elif choice == "6":
            print("Exiting system...")
            break
        else:
            print("Invalid choice. Try again.")
            
# Run the Menu

main_menu()



