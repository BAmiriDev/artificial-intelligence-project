"""
Task 2: Data Structures and Algorithms
Implementation of graph-based data structure for vaccination network analysis
"""

import heapq
from typing import Dict, List, Optional, Tuple, Set
from collections import defaultdict, deque
import matplotlib.pyplot as plt
import networkx as nx


class VaccinationGraph:
    """
    Graph data structure to model vaccination distribution networks
    
    Nodes represent countries/locations
    Edges represent connections (e.g., vaccine sharing, supply routes)
    """
    
    def __init__(self):
        """Initialize empty graph structure"""
        # Adjacency list representation for efficient neighbor access
        # Format: {node: {neighbor: weight, ...}, ...}
        self.adjacency_list: Dict[str, Dict[str, float]] = defaultdict(dict)
        
        # Store node attributes (e.g., population, vaccination rate)
        self.node_attributes: Dict[str, Dict] = {}
    
    def add_country(self, country: str, attributes: Dict = None) -> None:
        """
        Add a country/location node to the graph

        """
        if country not in self.adjacency_list:
            self.adjacency_list[country] = {}
        
        if attributes:
            self.node_attributes[country] = attributes
    
    def add_connection(self, country1: str, country2: str, weight: float = 1.0) -> None:
        """
        Add undirected edge between two countries
        """
        # Ensure both nodes exist
        self.add_country(country1)
        self.add_country(country2)
        
        # Add bidirectional edge
        self.adjacency_list[country1][country2] = weight
        self.adjacency_list[country2][country1] = weight
    
    def get_countries(self) -> List[str]:
        """
        Get list of all countries in the graph
        """
        return list(self.adjacency_list.keys())
    
    def has_connection(self, country1: str, country2: str) -> bool:
        """
        Check if two countries are directly connected

        """
        return country2 in self.adjacency_list.get(country1, {})
    
    def get_neighbors(self, country: str) -> List[str]:
        """
        Get all countries directly connected to the given country
        """
        return list(self.adjacency_list.get(country, {}).keys())
    
    def shortest_path(self, start: str, end: str) -> Optional[List[str]]:
        """
        Find shortest path between two countries using Dijkstra's algorithm
        """
        if start not in self.adjacency_list or end not in self.adjacency_list:
            return None
        
        # Priority queue: (distance, current_node, path)
        pq = [(0, start, [start])]
        visited = set()
        
        while pq:
            current_dist, current_node, path = heapq.heappop(pq)
            
            if current_node in visited:
                continue
            
            if current_node == end:
                return path
            
            visited.add(current_node)
            
            # Explore neighbors
            for neighbor, weight in self.adjacency_list[current_node].items():
                if neighbor not in visited:
                    new_dist = current_dist + weight
                    new_path = path + [neighbor]
                    heapq.heappush(pq, (new_dist, neighbor, new_path))
        
        return None  # No path found
    
    def bfs_traversal(self, start: str) -> List[str]:
        """
        Breadth-First Search traversal from starting country
        """
        if start not in self.adjacency_list:
            return []
        
        visited = set()
        queue = deque([start])
        result = []
        
        while queue:
            current = queue.popleft()
            
            if current in visited:
                continue
            
            visited.add(current)
            result.append(current)
            
            # Add unvisited neighbors to queue
            for neighbor in self.adjacency_list[current]:
                if neighbor not in visited:
                    queue.append(neighbor)
        
        return result
    
    def dfs_traversal(self, start: str) -> List[str]:
        """
        Depth-First Search traversal from starting country
        """
        if start not in self.adjacency_list:
            return []
        
        visited = set()
        result = []
        
        def dfs_helper(node: str):
            if node in visited:
                return
            
            visited.add(node)
            result.append(node)
            
            for neighbor in self.adjacency_list[node]:
                dfs_helper(neighbor)
        
        dfs_helper(start)
        return result
    
    def find_central_hubs(self, top_n: int = 5) -> List[Tuple[str, int]]:
        """
        Find most connected countries (highest degree centrality)
        """
        # Calculate degree (number of connections) for each node
        degrees = [(country, len(neighbors)) 
                   for country, neighbors in self.adjacency_list.items()]
        
        # Sort by degree in descending order
        degrees.sort(key=lambda x: x[1], reverse=True)
        
        return degrees[:top_n]
    
    def detect_communities(self) -> List[Set[str]]:
        """
        Detect connected components (communities) in the graph
        """
        visited = set()
        communities = []
        
        for country in self.adjacency_list:
            if country not in visited:
                # Find all countries in this component using BFS
                component = set()
                queue = deque([country])
                
                while queue:
                    current = queue.popleft()
                    if current in visited:
                        continue
                    
                    visited.add(current)
                    component.add(current)
                    
                    for neighbor in self.adjacency_list[current]:
                        if neighbor not in visited:
                            queue.append(neighbor)
                
                communities.append(component)
        
        return communities
    
    def visualize(self, title: str = "Vaccination Network", save_path: str = None) -> None:
        """
        Visualize the graph using matplotlib and networkx
        """
        # Create NetworkX graph from adjacency list
        G = nx.Graph()
        
        for country, neighbors in self.adjacency_list.items():
            for neighbor, weight in neighbors.items():
                G.add_edge(country, neighbor, weight=weight)
        
        # Create visualization
        plt.figure(figsize=(14, 10))
        
        # Use spring layout for better visualization
        pos = nx.spring_layout(G, k=0.5, iterations=50)
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, 
                              node_color='lightblue',
                              node_size=1000,
                              alpha=0.9)
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, 
                              width=2,
                              alpha=0.5,
                              edge_color='gray')
        
        # Draw labels
        nx.draw_networkx_labels(G, pos, 
                               font_size=10,
                               font_weight='bold')
        
        plt.title(title, fontsize=16, fontweight='bold')
        plt.axis('off')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Graph visualization saved to: {save_path}")
        
        plt.show()


class VaccinationQueue:
    """
    Priority Queue for managing vaccination appointments
    """
    
    def __init__(self):
        """Initialize empty priority queue"""
        self.heap = []
        self.counter = 0  # To break ties in priority
    
    def add_person(self, name: str, priority: int, age: int, category: str) -> None:
        """
        Add person to vaccination queue
        """
        # Use counter to ensure stable ordering (FIFO for same priority)
        entry = (priority, self.counter, name, age, category)
        heapq.heappush(self.heap, entry)
        self.counter += 1
    
    def get_next_person(self) -> Optional[Tuple[str, int, str]]:
        """
        Get next person to vaccinate (highest priority)
        """
        if self.heap:
            priority, counter, name, age, category = heapq.heappop(self.heap)
            return (name, age, category)
        return None
    
    def peek(self) -> Optional[Tuple[str, int, str]]:
        """
        View next person without removing from queue
        """
        if self.heap:
            priority, counter, name, age, category = self.heap[0]
            return (name, age, category)
        return None
    
    def size(self) -> int:
        """Get number of people in queue"""
        return len(self.heap)
    
    def is_empty(self) -> bool:
        """Check if queue is empty"""
        return len(self.heap) == 0


# Demonstration and testing functions
def demo_vaccination_graph():
    """Demonstrate graph functionality with realistic vaccine distribution example"""
    print("\n" + "="*70)
    print("TASK 2: VACCINATION NETWORK GRAPH DEMONSTRATION")
    print("="*70)
    
    # Create graph representing vaccine distribution network
    graph = VaccinationGraph()
    
    # Add countries with attributes
    countries = {
        "USA": {"population": 331000000, "vaccination_rate": 0.75},
        "Canada": {"population": 38000000, "vaccination_rate": 0.80},
        "Mexico": {"population": 128000000, "vaccination_rate": 0.60},
        "UK": {"population": 67000000, "vaccination_rate": 0.78},
        "France": {"population": 65000000, "vaccination_rate": 0.76},
        "Germany": {"population": 83000000, "vaccination_rate": 0.74},
        "India": {"population": 1380000000, "vaccination_rate": 0.65},
        "China": {"population": 1440000000, "vaccination_rate": 0.85},
        "Japan": {"population": 126000000, "vaccination_rate": 0.82},
        "Australia": {"population": 26000000, "vaccination_rate": 0.79}
    }
    
    for country, attrs in countries.items():
        graph.add_country(country, attrs)
    
    # Add connections (vaccine sharing agreements, supply routes)
    # Lower weight = stronger connection/easier distribution
    connections = [
        ("USA", "Canada", 1),
        ("USA", "Mexico", 2),
        ("USA", "UK", 3),
        ("Canada", "UK", 4),
        ("UK", "France", 1),
        ("UK", "Germany", 2),
        ("France", "Germany", 1),
        ("Germany", "India", 5),
        ("India", "China", 3),
        ("China", "Japan", 2),
        ("Japan", "Australia", 3),
        ("USA", "Japan", 5)
    ]
    
    for c1, c2, weight in connections:
        graph.add_connection(c1, c2, weight)
    
    print("\n1. GRAPH STRUCTURE")
    print(f"   Total countries: {len(graph.get_countries())}")
    print(f"   Total connections: {sum(len(neighbors) for neighbors in graph.adjacency_list.values()) // 2}")
    
    # Find shortest path
    print("\n2. SHORTEST PATH ALGORITHM (Dijkstra)")
    start, end = "USA", "Australia"
    path = graph.shortest_path(start, end)
    print(f"   Optimal vaccine route from {start} to {end}:")
    print(f"   → {' → '.join(path)}")
    print(f"   Total hops: {len(path) - 1}")
    
    # BFS traversal
    print("\n3. BREADTH-FIRST SEARCH")
    bfs_result = graph.bfs_traversal("USA")
    print(f"   Countries reachable from USA (BFS order):")
    print(f"   {' → '.join(bfs_result[:5])}...")
    
    # Find central hubs
    print("\n4. CENTRAL VACCINE DISTRIBUTION HUBS")
    hubs = graph.find_central_hubs(5)
    print("   Top 5 most connected countries:")
    for country, connections_count in hubs:
        print(f"   - {country}: {connections_count} connections")
    
    # Detect communities
    print("\n5. NETWORK COMMUNITIES")
    communities = graph.detect_communities()
    print(f"   Number of separate networks: {len(communities)}")
    for i, community in enumerate(communities, 1):
        print(f"   Community {i}: {', '.join(list(community)[:5])}...")
    
    # Visualize
    print("\n6. GRAPH VISUALIZATION")
    try:
        graph.visualize(title="Global Vaccination Distribution Network",
                       save_path="exports/vaccination_network.png")
    except Exception as e:
        print(f"   Visualization skipped: {str(e)}")
    
    print("\n" + "="*70)
    
    return graph


def demo_vaccination_queue():
    """Demonstrate priority queue for vaccination scheduling"""
    print("\n" + "="*70)
    print("VACCINATION PRIORITY QUEUE DEMONSTRATION")
    print("="*70)
    
    queue = VaccinationQueue()
    
    # Add people with different priorities
    # Priority: 1=healthcare, 2=elderly/high-risk, 3=general population
    people = [
        ("John Doe", 3, 35, "general"),
        ("Dr. Smith", 1, 45, "healthcare"),
        ("Mary Johnson", 2, 78, "elderly"),
        ("Bob Williams", 3, 28, "general"),
        ("Nurse Davis", 1, 32, "healthcare"),
        ("Sarah Miller", 2, 82, "elderly"),
        ("Tom Brown", 3, 50, "general"),
    ]
    
    print("\n1. ADDING PEOPLE TO QUEUE")
    for name, priority, age, category in people:
        queue.add_person(name, priority, age, category)
        print(f"   Added: {name} (Priority: {priority}, Age: {age}, Category: {category})")
    
    print(f"\n   Total in queue: {queue.size()}")
    
    print("\n2. PROCESSING VACCINATIONS (by priority)")
    print("   Order of vaccination:")
    position = 1
    while not queue.is_empty():
        person = queue.get_next_person()
        if person:
            name, age, category = person
            print(f"   {position}. {name} - {category} (age {age})")
            position += 1
    
    print("\n" + "="*70)


if __name__ == "__main__":
    # Run demonstrations
    demo_vaccination_graph()
    demo_vaccination_queue()
    
    print("\n✓ Task 2 demonstrations completed successfully!")
