**RouteLink: Logistic Scheduling and Tracking Delivery System**

**UN SDG 9: Industry, Innovation, and Infrastructure**

## Project Description

A Python-based logistics delivery system that addresses inefficient manual scheduling, lack of real-time tracking, and difficulty in data-driven management for small to medium-scale delivery operations.

**Core Data Structures:**
- **Dynamic Array**: Stores delivery records with O(1) append operations
- **Queue (Deque)**: FIFO scheduling for automatic dispatch management
- **Graph (Tree)**: BFS pathfinding from warehouse to delivery destinations
- **Quick Sort & Group Sort**: Organizes deliveries by destination and multi-level status sorting
- **Hash Tables**: O(1) lookups for travel times, status mappings, and dynamic grouping

## Installation/Setup


## Usage Instructions

1. **Register Delivery**: Enter parcel ID, sender, receiver, and destination. First delivery auto-dispatches; others queue as pending.

2. **Update Status**: Select a parcel ID and change status (Pending → Dispatched → Out for Delivery → Delivered). System auto-dispatches next pending delivery upon completion.

3. **View Status Report**: Filter deliveries by status with group sorting (status then destination).

4. **Quick Sort Deliveries**: View all deliveries sorted alphabetically by destination.

5. **Show Route Map**: Display graph structure and completed delivery routes with travel times.

