class FlowTable:
    def __init__(self):
        self.flows = {}

    def add_flow(self, flow_id, flow_details):
        self.flows[flow_id] = flow_details

    def remove_flow(self, flow_id):
        if flow_id in self.flows:
            del self.flows[flow_id]

    def list_flows(self):
        return self.flows