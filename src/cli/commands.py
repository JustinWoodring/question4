def add_switch(controller, switch_id):
    controller.add_switch(switch_id)
    print(f"Switch {switch_id} added.")

def list_flows(controller):
    flows = controller.flow_table.list_flows()
    if flows:
        print("Current flows:")
        for flow in flows:
            print(flow)
    else:
        print("No flows found.")

def compute_path(controller, start, end):
    path = controller.compute_shortest_path(start, end)
    if path:
        print(f"Shortest path from {start} to {end}: {' -> '.join(path)}")
    else:
        print(f"No path found from {start} to {end}.")

def start_cli(controller):
    """
    Start the command-line interface for the SDN controller.
    
    Args:
        controller: The SDN controller instance
    """
    print("SDN Controller CLI")
    print("Type 'help' for available commands")
    
    commands = {
        "add_switch": {"func": add_switch, "args": ["switch_id"], "help": "Add a new switch to the network"},
        "add_link": {"func": controller.add_link, "args": ["source", "destination", "bandwidth"], 
                     "help": "Add a link between two switches"},
        "remove_link": {"func": controller.remove_link, "args": ["source", "destination"],
                       "help": "Remove a link between two switches"},
        "list_switches": {"func": controller.list_switches, "args": [], 
                         "help": "List all switches in the network"},
        "list_flows": {"func": list_flows, "args": [], "help": "List all active flows"},
        "add_flow": {"func": controller.add_flow, "args": ["source", "destination", "bandwidth", "priority"],
                    "help": "Add a new flow between source and destination"},
        "compute_path": {"func": compute_path, "args": ["start", "end"], 
                        "help": "Compute shortest path between two nodes"},
        "simulate_failure": {"func": controller.simulate_link_failure, "args": ["source", "destination"],
                            "help": "Simulate a link failure between two switches"},
        "show_topology": {"func": controller.visualize_topology, "args": [],
                         "help": "Display the current network topology"},
        "show_stats": {"func": controller.show_link_stats, "args": [],
                      "help": "Show link utilization statistics"},
        "exit": {"func": None, "args": [], "help": "Exit the CLI"}
    }
    
    while True:
        try:
            user_input = input("> ").strip()
            
            if not user_input:
                continue
                
            parts = user_input.split()
            cmd = parts[0].lower()
            args = parts[1:]
            
            if cmd == "help":
                print("Available commands:")
                for command, details in commands.items():
                    arg_str = " ".join([f"<{arg}>" for arg in details["args"]])
                    print(f"  {command} {arg_str} - {details['help']}")
                continue
                
            if cmd == "exit":
                print("Exiting CLI...")
                break
                
            if cmd not in commands:
                print(f"Unknown command: {cmd}")
                print("Type 'help' to see available commands")
                continue
                
            command = commands[cmd]
            if len(args) != len(command["args"]):
                print(f"Invalid arguments. Usage: {cmd} {' '.join([f'<{arg}>' for arg in command['args']])}")
                continue
                
            # Convert numeric arguments if needed
            processed_args = []
            for i, arg in enumerate(args):
                if command["args"][i].endswith(("bandwidth", "priority")):
                    try:
                        processed_args.append(float(arg))
                    except ValueError:
                        print(f"Error: {command['args'][i]} must be a number")
                        break
                else:
                    processed_args.append(arg)
            else:
                # If the command is add_switch or compute_path, handle differently
                if cmd == "add_switch":
                    add_switch(controller, processed_args[0])
                elif cmd == "list_flows":
                    list_flows(controller)
                elif cmd == "compute_path":
                    compute_path(controller, processed_args[0], processed_args[1])
                else:
                    # For other commands, call the function directly
                    command["func"](*processed_args)
        
        except KeyboardInterrupt:
            print("\nExiting CLI...")
            break
        except Exception as e:
            print(f"Error: {str(e)}")