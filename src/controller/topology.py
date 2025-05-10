import matplotlib.pyplot as plt
from collections import defaultdict
import heapq

class Topology:
    def __init__(self):
        """Initialize an empty network topology."""
        self.nodes = set()
        self.edges = {}  # {(src, dst): {'bandwidth': value, 'weight': value}}
        self.adjacency = defaultdict(list)  # {node: [neighbors]}
        
    def add_node(self, node_id):
        """Add a node to the topology."""
        if node_id not in self.nodes:
            self.nodes.add(node_id)
            return True
        return False
        
    def add_edge(self, source, destination, bandwidth):
        """Add an edge between two nodes with given bandwidth."""
        if source not in self.nodes:
            self.add_node(source)
        if destination not in self.nodes:
            self.add_node(destination)
            
        # Add forward edge
        self.edges[(source, destination)] = {
            'bandwidth': bandwidth,
            'weight': 1/bandwidth  # Inverse of bandwidth for shortest path calculation
        }
        self.adjacency[source].append(destination)
        
        # Add reverse edge for bidirectional links
        self.edges[(destination, source)] = {
            'bandwidth': bandwidth,
            'weight': 1/bandwidth
        }
        self.adjacency[destination].append(source)
        
    def remove_edge(self, source, destination):
        """Remove an edge from the topology."""
        if self.has_edge(source, destination):
            # Remove forward edge
            if (source, destination) in self.edges:
                del self.edges[(source, destination)]
            if destination in self.adjacency[source]:
                self.adjacency[source].remove(destination)
                
            # Remove reverse edge
            if (destination, source) in self.edges:
                del self.edges[(destination, source)]
            if source in self.adjacency[destination]:
                self.adjacency[destination].remove(source)
            return True
        return False
        
    def has_edge(self, source, destination):
        """Check if an edge exists between source and destination."""
        return (source, destination) in self.edges
        
    def get_nodes(self):
        """Get all nodes in the topology."""
        return list(self.nodes)
        
    def get_edges(self):
        """Get all edges in the topology."""
        return list(self.edges.keys())
        
    def get_shortest_path(self, source, destination):
        """Compute the shortest path between source and destination using Dijkstra's algorithm."""
        if source not in self.nodes or destination not in self.nodes:
            return None
            
        # Initialize distances and previous nodes
        distances = {node: float('infinity') for node in self.nodes}
        distances[source] = 0
        previous = {node: None for node in self.nodes}
        
        # Priority queue for Dijkstra's algorithm
        priority_queue = [(0, source)]
        
        while priority_queue:
            current_distance, current_node = heapq.heappop(priority_queue)
            
            # If we reached the destination, reconstruct and return the path
            if current_node == destination:
                path = []
                while current_node:
                    path.append(current_node)
                    current_node = previous[current_node]
                return path[::-1]  # Reverse to get path from source to destination
                
            # If we've found a longer path to the current node, skip
            if current_distance > distances[current_node]:
                continue
                
            # Check all neighbors
            for neighbor in self.adjacency[current_node]:
                edge = (current_node, neighbor)
                if edge in self.edges:
                    weight = self.edges[edge]['weight']
                    distance = current_distance + weight
                    
                    # If we found a shorter path to the neighbor
                    if distance < distances[neighbor]:
                        distances[neighbor] = distance
                        previous[neighbor] = current_node
                        heapq.heappush(priority_queue, (distance, neighbor))
        
        # If we get here, there's no path to the destination
        return None
            
    def get_all_paths(self, source, destination, k=3):
        """Get up to k paths between source and destination."""
        if source not in self.nodes or destination not in self.nodes:
            return []
            
        # Use a simple DFS to find paths
        def dfs_paths(current, dest, path, visited, all_paths):
            # Mark the current node as visited
            visited.add(current)
            path.append(current)
            
            # If current node is the destination, add path to results
            if current == dest:
                all_paths.append(path.copy())
            else:
                # Try all neighbors
                for neighbor in self.adjacency[current]:
                    if neighbor not in visited:
                        dfs_paths(neighbor, dest, path, visited, all_paths)
                        
            # Backtrack
            path.pop()
            visited.remove(current)
            
        all_paths = []
        dfs_paths(source, destination, [], set(), all_paths)
        
        # Sort paths by total weight (sum of edge weights)
        def path_weight(path):
            total = 0
            for i in range(len(path) - 1):
                edge = (path[i], path[i+1])
                total += self.edges[edge]['weight']
            return total
            
        all_paths.sort(key=path_weight)
        return all_paths[:k]
        
    def visualize(self, link_stats=None, active_flows=None):
        """Visualize the network topology with link utilization and active flows."""
        if not self.nodes:
            print("Network is empty, nothing to visualize.")
            return
        
        print("NetworkX or matplotlib not available for visualization.")
        print("Current topology:")
        print(f"Nodes: {self.nodes}")
        print("Edges:")
        for edge, data in self.edges.items():
            src, dst = edge
            bw = data['bandwidth']
            print(f"  {src} → {dst} (bandwidth: {bw})")