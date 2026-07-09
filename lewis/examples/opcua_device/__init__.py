from lewis.adapters import OPCUAAdapter
from lewis.devices import Device

class OPCUADevice(Device):
    pass

class ExampleOPCUADevice(OPCUAAdapter):
    """Interface for my device."""
    
    def __init__(self):
        self.temperature = 25.0
        self.power = False
    
    def set_temperature(self, value):
        """Set the temperature."""
        self.temperature = float(value)
        return True
    
    def reset(self):
        """Reset the device."""
        self.temperature = 25.0
        self.power = False
        return True

# Configuration for the adapter
opcua_adapter = {
    'options': {
        'port': 4840,
        'server_name': 'My Device OPC UA Server',
        'read_only_properties': ['status']
    }
}