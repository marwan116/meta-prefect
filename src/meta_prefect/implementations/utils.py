import uuid


def get_machine_id() -> str:
    # Get the MAC address of the first network interface
    mac_address = uuid.getnode()

    # Generate a UUID based on the MAC address
    machine_id = uuid.UUID(int=mac_address)

    # Print the machine ID
    return str(machine_id)
