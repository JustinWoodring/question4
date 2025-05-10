class Switch:
    def __init__(self, switch_id):
        self.switch_id = switch_id
        self.ports = []

    def add_port(self, port):
        if port not in self.ports:
            self.ports.append(port)

    def remove_port(self, port):
        if port in self.ports:
            self.ports.remove(port)

    def get_ports(self):
        return self.ports

    def __repr__(self):
        return f"Switch(id={self.switch_id}, ports={self.ports})"