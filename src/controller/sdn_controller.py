from controller.topology import Topology

#My supercool hash: c2580be5458f4d194050d82cadd899e8e22c8ef869bc98ca264e8fa9e65a5a99

class SDNController:
    def __init__(self):
        self.topology = Topology()
        self.flow_table = FlowTable()
        self.active_flows = {}
        self.link_stats = {}
        
    def add_switch(self, switch_id):
        """Add a switch to the network topology."""
        self.topology.add_node(switch_id)
        
    def add_link(self, source, destination, bandwidth):
        """Add a link between two switches with specified bandwidth."""
        self.topology.add_edge(source, destination, bandwidth=bandwidth)
        # Initialize link statistics
        link_id = (source, destination)
        self.link_stats[link_id] = {
            'bandwidth': bandwidth,
            'utilization': 0,
            'flows': []
        }
        print(f"Link added between {source} and {destination} with bandwidth {bandwidth}")
        
    def remove_link(self, source, destination):
        """Remove a link between two switches."""
        self.topology.remove_edge(source, destination)
        # Remove link statistics
        link_id = (source, destination)
        if link_id in self.link_stats:
            del self.link_stats[link_id]
        # Reconfigure affected flows
        self._reconfigure_affected_flows(source, destination)
        print(f"Link removed between {source} and {destination}")
        
    def list_switches(self):
        """List all switches in the network."""
        switches = self.topology.get_nodes()
        if switches:
            print("Switches in the network:")
            for switch in switches:
                print(f"  - {switch}")
        else:
            print("No switches in the network.")
        
    def compute_shortest_path(self, source, destination):
        """Compute the shortest path between source and destination."""
        return self.topology.get_shortest_path(source, destination)
        
    def add_flow(self, source, destination, bandwidth, priority):
        """Add a new flow between source and destination."""
        # Compute path for the flow
        path = self.compute_shortest_path(source, destination)
        if not path:
            print(f"Cannot add flow: no path exists between {source} and {destination}")
            return
            
        flow_id = f"flow-{source}-{destination}-{len(self.active_flows)}"
        flow = {
            'id': flow_id,
            'source': source,
            'destination': destination,
            'path': path,
            'bandwidth': bandwidth,
            'priority': priority
        }
        
        # Add flow to active flows
        self.active_flows[flow_id] = flow
        
        # Update link utilization
        self._update_link_stats(flow, add=True)
        
        # Generate flow table entries
        self._generate_flow_entries(flow)
        
        print(f"Flow {flow_id} added from {source} to {destination} with priority {priority}")
        
    def simulate_link_failure(self, source, destination):
        """Simulate a link failure between two switches."""
        print(f"Simulating failure of link between {source} and {destination}")
        # Temporarily remove the link
        if self.topology.has_edge(source, destination):
            self.remove_link(source, destination)
            # Reconfigure affected flows
            self._reconfigure_affected_flows(source, destination)
        else:
            print(f"No link exists between {source} and {destination}")
            
    def visualize_topology(self):
        """Visualize the network topology."""
        self.topology.visualize(self.link_stats, self.active_flows)
        
    def show_link_stats(self):
        """Show link utilization statistics."""
        if not self.link_stats:
            print("No links in the network.")
            return
            
        print("Link Utilization Statistics:")
        print("----------------------------")
        for link, stats in self.link_stats.items():
            source, dest = link
            util_percent = (stats['utilization'] / stats['bandwidth']) * 100 if stats['bandwidth'] > 0 else 0
            print(f"{source} → {dest}: {util_percent:.2f}% utilized ({stats['utilization']}/{stats['bandwidth']})")
            if stats['flows']:
                print(f"  Flows: {', '.join(stats['flows'])}")
                
    def _update_link_stats(self, flow, add=True):
        """Update link statistics for a flow."""
        path = flow['path']
        bandwidth = flow['bandwidth']
        flow_id = flow['id']
        
        # Update statistics for each link in the path
        for i in range(len(path) - 1):
            source, dest = path[i], path[i+1]
            link_id = (source, dest)
            
            if link_id in self.link_stats:
                if add:
                    self.link_stats[link_id]['utilization'] += bandwidth
                    self.link_stats[link_id]['flows'].append(flow_id)
                else:
                    self.link_stats[link_id]['utilization'] = max(0, self.link_stats[link_id]['utilization'] - bandwidth)
                    if flow_id in self.link_stats[link_id]['flows']:
                        self.link_stats[link_id]['flows'].remove(flow_id)
                        
    def _reconfigure_affected_flows(self, source, destination):
        """Reconfigure flows affected by a link failure."""
        affected_flows = []
        link_id = (source, destination)
        
        # Find flows that use the failed link
        for flow_id, flow in self.active_flows.items():
            path = flow['path']
            for i in range(len(path) - 1):
                if (path[i], path[i+1]) == link_id:
                    affected_flows.append(flow_id)
                    break
                    
        # Reconfigure each affected flow
        for flow_id in affected_flows:
            flow = self.active_flows[flow_id]
            # Remove flow statistics from old path
            self._update_link_stats(flow, add=False)
            
            # Compute new path
            new_path = self.compute_shortest_path(flow['source'], flow['destination'])
            if new_path:
                # Update flow with new path
                flow['path'] = new_path
                # Update flow statistics for new path
                self._update_link_stats(flow, add=True)
                # Update flow table entries
                self._generate_flow_entries(flow)
                print(f"Flow {flow_id} reconfigured with new path: {' -> '.join(new_path)}")
            else:
                # Remove flow if no alternative path exists
                del self.active_flows[flow_id]
                print(f"Flow {flow_id} removed: no alternative path available")
                
    def _generate_flow_entries(self, flow):
        """Generate flow table entries for switches along the path."""
        path = flow['path']
        flow_id = flow['id']
        
        print(f"Generating flow table entries for {flow_id}")
        for i in range(len(path) - 1):
            switch = path[i]
            next_hop = path[i+1]
            # Create flow table entry
            entry = {
                'switch': switch,
                'match': {
                    'src': flow['source'],
                    'dst': flow['destination']
                },
                'action': {
                    'forward': next_hop
                },
                'priority': flow['priority']
            }
            
            # Add entry to flow table
            self.flow_table.add_entry(entry)
            print(f"  Switch {switch}: Forward {flow['source']}→{flow['destination']} to {next_hop}")


class FlowTable:
    def __init__(self):
        self.entries = []
        
    def add_entry(self, entry):
        """Add a flow table entry."""
        self.entries.append(entry)
        
    def remove_entries_for_switch(self, switch_id):
        """Remove all entries for a specific switch."""
        self.entries = [entry for entry in self.entries if entry['switch'] != switch_id]
        
    def list_flows(self):
        """List all flow table entries."""
        if not self.entries:
            return []
            
        result = []
        for entry in self.entries:
            src = entry['match']['src']
            dst = entry['match']['dst']
            switch = entry['switch']
            action = entry['action']['forward']
            priority = entry['priority']
            result.append(f"Switch {switch}: {src}→{dst} via {action} (priority: {priority})")
        return result