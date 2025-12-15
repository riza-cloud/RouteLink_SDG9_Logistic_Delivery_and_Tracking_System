from collections import deque

# ============================================
# DELIVERY CLASS (Core Data Module)
# ============================================
class Delivery:
    """Represents a single delivery record"""
    
    def __init__(self, parcel_id, sender, receiver, destination, status="Pending"):
        self.id = parcel_id
        self.sender = sender
        self.receiver = receiver
        self.destination = destination
        self.status = status
    
    def to_dict(self):
        """Convert delivery to dictionary format"""
        return {
            "id": self.id,
            "sender": self.sender,
            "receiver": self.receiver,
            "destination": self.destination,
            "status": self.status
        }
    
    def update_status(self, new_status):
        """Update the delivery status"""
        self.status = new_status


# ============================================
# DELIVERY MANAGER CLASS (Data Management)
# ============================================
class DeliveryManager:
    """Manages all delivery records and operations"""
    
    def __init__(self):
        self.deliveries = []
        self.completed_deliveries = []
        self.status_options = {
            "1": "Pending",
            "2": "Dispatched",
            "3": "Out for Delivery",
            "4": "Delivered"
        }
    
    def add_delivery(self, delivery):
        """Add a new delivery to the system"""
        self.deliveries.append(delivery)
    
    def find_by_id(self, parcel_id):
        """Find a delivery by ID"""
        for delivery in self.deliveries:
            if delivery.id == parcel_id:
                return delivery
        return None
    
    def id_exists(self, parcel_id):
        """Check if a parcel ID already exists"""
        return any(d.id == parcel_id for d in self.deliveries)
    
    def get_active_delivery(self):
        """Get the currently active (non-pending, non-delivered) delivery"""
        for delivery in self.deliveries:
            if delivery.status in ["Dispatched", "Out for Delivery"]:
                return delivery
        return None
    
    def get_active_deliveries(self):
        """Get all active or pending deliveries"""
        return [d for d in self.deliveries if d.status != "Delivered"]
    
    def get_delivered(self):
        """Get all delivered items"""
        return [d for d in self.deliveries if d.status == "Delivered"]
    
    def filter_by_status(self, status):
        """Filter deliveries by status"""
        return [d for d in self.deliveries if d.status == status]
    
    def complete_delivery(self, delivery, route_graph):
        """Mark delivery as completed and record route info"""
        route = route_graph.find_route(delivery.destination)
        route_str = " -> ".join(route) if route else "N/A"
        travel_time = route_graph.calculate_travel_time(route) if route else 0
        
        completed_record = {
            "id": delivery.id,
            "sender": delivery.sender,
            "receiver": delivery.receiver,
            "origin": "Warehouse",
            "destination": delivery.destination,
            "route": route_str,
            "time": travel_time,
            "status": "Delivered"
        }
        self.completed_deliveries.append(completed_record)


# ============================================
# SCHEDULER CLASS (Queue Management)
# ============================================
class Scheduler:
    """Manages delivery scheduling queue"""
    
    def __init__(self):
        self.schedule_queue = deque()
    
    def add_to_queue(self, delivery):
        """Add a delivery to the scheduling queue"""
        self.schedule_queue.append(delivery)
    
    def dispatch_next_pending(self):
        """Automatically dispatch the next pending delivery in queue"""
        for delivery in self.schedule_queue:
            if delivery.status == "Pending":
                delivery.update_status("Dispatched")
                return delivery
        return None


# ============================================
# ROUTE GRAPH CLASS
# ============================================
class RouteGraph:
    """Manages delivery routes and travel times"""
    
    def __init__(self):
        self.routes = {
            "Warehouse": ["Area A", "Area B"],
            "Area A": ["Area C", "Area D"],
            "Area B": ["Area E", "Area F"],
            "Area C": [],
            "Area D": [],
            "Area E": [],
            "Area F": []
        }
        
        self.travel_times = {
            ("Warehouse", "Area A"): 3,
            ("Warehouse", "Area B"): 4,
            ("Area A", "Area C"): 3,
            ("Area A", "Area D"): 3,
            ("Area B", "Area E"): 4,
            ("Area B", "Area F"): 4
        }
    
    def find_route(self, destination):
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
            
            for child in self.routes.get(current, []):
                if child not in visited:
                    queue.append((child, path + [child]))
        
        return []
    
    def calculate_travel_time(self, route):
        """Calculate total travel time for a route"""
        total_time = 0
        for i in range(len(route) - 1):
            edge = (route[i], route[i+1])
            total_time += self.travel_times.get(edge, 0)
        return total_time
    
    def get_route_map(self):
        """Return the route map"""
        return self.routes


# ============================================
# SORTING MODULE CLASS
# ============================================
class SortingModule:
    """Handles all sorting operations for deliveries"""
    
    @staticmethod
    def quick_sort(arr, key):
        """Quick sort algorithm for sorting by a specific key"""
        if len(arr) <= 1:
            return arr
        
        pivot = arr[0]
        pivot_val = getattr(pivot, key) if hasattr(pivot, key) else pivot.get(key)
        
        if pivot_val is None:
            return arr
        
        left = [x for x in arr if (getattr(x, key) if hasattr(x, key) else x.get(key)) < pivot_val]
        middle = [x for x in arr if (getattr(x, key) if hasattr(x, key) else x.get(key)) == pivot_val]
        right = [x for x in arr if (getattr(x, key) if hasattr(x, key) else x.get(key)) > pivot_val]
        
        return SortingModule.quick_sort(left, key) + middle + SortingModule.quick_sort(right, key)
    
    @staticmethod
    def group_sort(arr, primary_key, secondary_key, status_options):
        """Sorts deliveries first by primary key, then by secondary key"""
        groups = {}
        for item in arr:
            key = getattr(item, primary_key) if hasattr(item, primary_key) else item.get(primary_key)
            if key not in groups:
                groups[key] = []
            groups[key].append(item)
        
        final_sorted_list = []
        status_order = {status: i for i, status in enumerate(status_options.values())}
        sorted_groups_keys = sorted(groups.keys(), key=lambda k: status_order.get(k, 99))
        
        for key in sorted_groups_keys:
            sorted_group = SortingModule.quick_sort(groups[key], secondary_key)
            final_sorted_list.extend(sorted_group)
        
        return final_sorted_list


# ============================================
# USER INTERFACE CLASS (Presentation Module)
# ============================================
class UserInterface:
    """Handles all user interactions and display"""
    
    def __init__(self, delivery_manager, scheduler, route_graph):
        self.delivery_manager = delivery_manager
        self.scheduler = scheduler
        self.route_graph = route_graph
    
    def register_delivery(self):
        """Register a new delivery"""
        print("\n--- Register Delivery ---")
        
        parcel_id = input("Enter Parcel ID: ")
        
        if self.delivery_manager.id_exists(parcel_id):
            print(f"Error: Parcel ID {parcel_id} already exists.")
            return
        
        sender = input("Enter Sender Name: ")
        receiver = input("Enter Receiver Name: ")
        destination = input("Enter Destination Location: ")
        
        active_delivery = self.delivery_manager.get_active_delivery()
        
        if active_delivery is None:
            status = "Dispatched"
            print(f"No active delivery found. Parcel {parcel_id} is now DISPATCHED!")
        else:
            status = "Pending"
            print(f"Delivery in progress (ID: {active_delivery.id}). Parcel {parcel_id} added to queue as PENDING.")
        
        delivery = Delivery(parcel_id, sender, receiver, destination, status)
        self.delivery_manager.add_delivery(delivery)
        self.scheduler.add_to_queue(delivery)
        print("Delivery Registered & Added to Queue!")
    
    def update_status(self):
        """Update delivery status"""
        print("\n--- Update Delivery Status ---")
        
        active_deliveries = self.delivery_manager.get_active_deliveries()
        
        if not active_deliveries:
            print("No active deliveries to update.")
            return
        
        print("\nActive Deliveries:")
        for d in active_deliveries:
            print(f"ID: {d.id} - Status: {d.status}")
        
        parcel_id = input("\nEnter Parcel ID to update: ")
        delivery = self.delivery_manager.find_by_id(parcel_id)
        
        if delivery is None:
            print("Parcel ID not found.")
            return
        
        print(f"Current Status: {delivery.status}")
        print("\nSelect New Status:")
        print("[1] Pending")
        print("[2] Dispatched")
        print("[3] Out for Delivery")
        print("[4] Delivered")
        
        choice = input("Enter choice (1-4): ")
        
        if choice in self.delivery_manager.status_options:
            old_status = delivery.status
            new_status = self.delivery_manager.status_options[choice]
            delivery.update_status(new_status)
            print(f"Status Updated to: {new_status}!")
            
            if new_status == "Delivered" and old_status in ["Dispatched", "Out for Delivery"]:
                self.delivery_manager.complete_delivery(delivery, self.route_graph)
                self.show_status_report()
                self.dispatch_next_pending()
        else:
            print("Invalid choice. Status not updated.")
    
    def dispatch_next_pending(self):
        """Automatically dispatch the next pending delivery"""
        next_delivery = self.scheduler.dispatch_next_pending()
        if next_delivery:
            print(f"\n>>> Next delivery auto-dispatched: ID {next_delivery.id} to {next_delivery.destination}")
        else:
            print("\n>>> No pending deliveries in queue.")
    
    def show_status_report(self):
        """Display all delivered items"""
        delivered = self.delivery_manager.get_delivered()
        
        if not delivered:
            print("\nNo deliveries completed today.")
            return
        
        print("\n--- Status Report: Delivered Today ---")
        print("-" * 85)
        print(f"{'ID':<10} {'Sender':<15} {'Receiver':<15} {'Destination':<15} {'Status':<10}")
        print("-" * 85)
        
        for d in delivered:
            print(f"{d.id:<10} {d.sender:<15} {d.receiver:<15} {d.destination:<15} {d.status:<10}")
        
        print("-" * 85)
    
    def view_status_report(self):
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
                filtered = self.delivery_manager.deliveries
                filter_name = "All Deliveries"
            elif choice in self.delivery_manager.status_options:
                status = self.delivery_manager.status_options[choice]
                filtered = self.delivery_manager.filter_by_status(status)
                filter_name = f"{status} Deliveries"
            else:
                print("Invalid choice. Try again.")
                continue
            
            if not filtered:
                print(f"\nNo {filter_name.lower()} found.")
                continue
            
            sorted_deliveries = SortingModule.quick_sort(filtered, key="destination")
            
            print(f"\n--- {filter_name} (Sorted by Destination) ---")
            print("-" * 95)
            print(f"{'ID':<10} {'Sender':<15} {'Receiver':<15} {'Destination':<15} {'Status':<15}")
            print("-" * 95)
            
            for d in sorted_deliveries:
                print(f"{d.id:<10} {d.sender:<15} {d.receiver:<15} {d.destination:<15} {d.status:<15}")
            
            print("-" * 95)
            print(f"Total: {len(sorted_deliveries)} deliveries")
    
    def sort_deliveries(self):
        """Sort and display deliveries by destination"""
        print("\n--- Sort Deliveries by Destination ---")
        sorted_list = SortingModule.quick_sort(self.delivery_manager.deliveries, key="destination")
        
        for d in sorted_list:
            print(f"{d.id} - {d.destination} - {d.status}")
    
    def show_map(self):
        """Display route map and completed deliveries"""
        print("\n--- Route Map (Graph) ---")
        route_map = self.route_graph.get_route_map()
        for place, connected in route_map.items():
            print(f"{place} -> {', '.join(connected) if connected else 'No outgoing routes'}")
        
        if not self.delivery_manager.completed_deliveries:
            print("\n--- Route Summary Table ---")
            print("No completed deliveries yet.")
            return
        
        print("\n--- Route Summary Table (Completed Deliveries Only) ---")
        print("-" * 90)
        print(f"{'ID':<10} {'Origin':<15} {'Destination':<15} {'Route':<30} {'Time (min)':<10}")
        print("-" * 90)
        
        for delivery in self.delivery_manager.completed_deliveries:
            print(f"{delivery['id']:<10} {delivery['origin']:<15} {delivery['destination']:<15} {delivery['route']:<30} {delivery['time']:<10}")
        
        print("-" * 90)
    
    def main_menu(self):
        """Display and handle main menu"""
        while True:
            print("\n" + "="*30)
            print(" LOGISTIC DELIVERY SYSTEM ")
            print("="*30)
            print("1. Register Delivery")
            print("2. Update Delivery Status")
            print("3. View Status Report")
            print("4. Quick Sort Deliveries")
            print("5. Show Route Map (Graph)")
            print("6. Exit")
            
            choice = input("Enter choice: ")
            
            if choice == "1":
                self.register_delivery()
            elif choice == "2":
                self.update_status()
            elif choice == "3":
                self.view_status_report()
            elif choice == "4":
                self.sort_deliveries()
            elif choice == "5":
                self.show_map()
            elif choice == "6":
                print("Exiting system...")
                break
            else:
                print("Invalid choice. Try again.")


# ============================================
# MAIN EXECUTION
# ============================================
if __name__ == "__main__":
    # Initialize all components
    delivery_manager = DeliveryManager()
    scheduler = Scheduler()
    route_graph = RouteGraph()
    ui = UserInterface(delivery_manager, scheduler, route_graph)
    
    # Run the application
    ui.main_menu()