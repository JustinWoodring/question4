from controller.sdn_controller import SDNController
from cli.commands import start_cli

def main():
    controller = SDNController()
    start_cli(controller)

if __name__ == "__main__":
    main()