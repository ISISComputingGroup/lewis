# -*- coding: utf-8 -*-
# *********************************************************************
# lewis - a library for creating hardware device simulators
# Copyright (C) 2016-2021 European Spallation Source ERIC
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# **

"""
This module provides components to expose a Device via a OPCUA Protocol. The following resources
were used as guidelines and references for implementing the protocol:

 - https://opcfoundation.org/wp-content/uploads/2014/05/OPC-UA_Security_EN.pdf
 - https://www.opc-router.com/what-is-opc-ua/
 - https://www.unified-automation.com/
 - https://github.com/bashwork/pymodbus

.. note::

    For an example how Modbus can be used in the current implementation, please look
    at lewis/examples/modbus_device.
"""

import asyncio
import inspect
import threading
import time
from typing import Any, Dict, Optional, List
from asyncua import Server, Node, ua
from asyncua.common.methods import uamethod

from lewis.core.adapters import Adapter
from lewis.core.devices import InterfaceBase
from lewis.core.logging import has_log

@has_log
class OPCUAAdapter(Adapter):
    """
    Adapter for exposing a device via OPCUA.
    
    This adapter creates an OPCUA server that exposes the device's
    properties and methods as OPCUA nodes. It handles mapping device properties to OPCUA
    noes and translating method calls from OPCUA to device method calls.

    :param options: Configuration options for the adapter.
    """

    default_options = {
        'port' : 4840, #Default OPCUA port
        'server_name': 'Lewis OPCUA Server',
        'uri': 'urn:lewis:opcua',
        'update_interval': 0.1, #Interval for updating variables in seconds
        'exclude_properties': [], #Properties excluded from exposure
        'read_only_properties': [], #Properties that should be read-only
        'security_mode' : 'None', #Security mode options: None, Sign, SignAndEncrypt
        'security_policy' : 'None', #Security policy options: None, Basic128Rsa15, Basic256, Basic256Sha256
        'certificate' : None, #Path to certificate
        'private_key' : None, #Path to private key file
    }

    protocol = 'opcua'

    def __init__(self, options: Optional[Dict[str, Any]] = None) -> None:
        """Initialise the OPCUA adapter with given options."""
        super(OPCUAAdapter, self).__init__(options)

        #Init member variables
        self._server = None
        self._running = False
        self._nodes = {}
        self._update_thread = None
        self._stop_event = threading.Event()

        #Track property values to detect changes
        self._property_values = {} 

    def start_server(self) -> None:
        """
        Start the OPCUA server.
        
        This method initialises the OPCUA server, creates the address space,
        populates it with nodes that represent device properties and methods,
        and starts the server.
        """

        if self._running:
            return
        
        #Create server
        self._server = Server()

        #Setup server parameters
        endpoint = F"opc.tcp://0.0.0.0:{self._options.port}"
        self._server.set_endpoint(endpoint)
        self._server.set_server_name(self._options.server_name)

        #Configure security if specified
        if (self._option.security_mode != 'None' and
                self._options.security_policy != 'None' and
                self._options.certificate and
                self._options.private_key):
            self._server.load_certificate(self._options.certificate)
            self._server.load_private_key(self._options.private_key)

            #Apply security settings
            security_string = f"{self._options.security_policy}, {self._options.security_mode}" 
            self._server.set_security_policy([security_string])

        #Setup namespace
        uri = self._option.uri
        idx = self._server.register_namespace(uri)

        #Create node to store the device
        objects = self._server.get_objects_node()
        device_node = objects.add_object(idx, "Device")

        #Add properties as variables and methods
        if self.interface:
            self._add_properties(idx, device_node)
            self._add_methods(idx, device_node)

        #Start the server
        self._server.start()
        self._running = True

        #Start the update thread for periodic property updates
        self._stop_event.clear()
        self._update_thread = threading.Thread(
            target=self._update_variables,
            daemon=True
        )
        self._update_thread.start()

        self.log.info(f"OPCUA Server started on {endpoint}")

    
    def _add_properties(self, idx: int, device_node: Node) -> None:
        """
        Add device properties as OPCUA variables.
        
        :param idx: Namespace index
        :param device_node: Device node to add the properties to
        """

        for property in dir(self.interface):
            #Skip the excluded properties, internal properties, and methods
            if (property in self._options.exclude_properties or
                    property.startswith('_') or
                    callable(getattr(self.interface, property))):
                continue
            
            #Get property value
            value = getattr(self.interface, property)

            #Determine if the property is writable
            writeable = property not in self._options.read_only_properties

            #Determine data type
            data_type = self._get_ua_data_type(value)

            #Create the variable node
            var = device_node.add_variable(
                idx,
                property,
                value,
                data_type
            )
            var.set_writeable(writeable)

            #Store the node for updates
            self._nodes[property] = var

            #Store initial value
            self._property_values[property] = value

            #If writeable, set up callback to handle writes
            if writeable:
                #definte write callback that updates the device
                def make_callback(property_name):
                    def write_callback(node, val):
                        with self.device_lock:
                            setattr(self.interface, property_name, val)
                        return True
                    return write_callback

                #set the callback
                var.set_value_callback = make_callback(property)

    
    def _add_methods(self, idx:int, device_node: Node) -> None:
        """
        Add device methods as OPCUA methods.
        
        :param idx: Namespace index
        :param device_node: Device node to add the methods to
        """

        for method_name in dir(self.interface):
            #Skip properties and internal/special methods
            if(not callable(getattr(self.interface, method_name)) or
                    method_name.startswith('_')):
                continue

            #Get the method
            method = getattr(self.interface, method_name)

            #Get info about the method's parameters
            try:
                signature = inspect.signature(method)

                #Create input argument descriptions
                inputs = []
                for param_name, param in signature.parameters.items():
                    if param_name == 'self':
                        continue

                    #Add input argument
                    inputs.append(ua.Argument(
                        name=param_name,
                        data_type=ua.NodeId(ua.ObjectIds.Variant),
                        value_rank=-1,
                        array_dimensions=[],
                        description=""
                    ))
                
                outputs = [
                    ua.Argument(
                        name="Result",
                        data_type=ua.NodeId(ua.ObjectIds.Variant),
                        value_rank=-1,
                        array_dimensions=[],
                        description=""
                    )
                ]

                #Create a wrapper to call the device method
                def method_wrapper(parent, *args):
                    with self.device_lock:
                        result = getattr(self.interface, method_name)(*args)
                        return [result] if result is not None else []
                    
                device_node.add_method(
                    idx,
                    method_name,
                    method_wrapper,
                    inputs,
                    outputs
                )
            except Exception as e:
                self.log.warning(f"Failed to add method {method_name}: {e}")

    def _get_ua_data_type(self, value: Any) -> ua.VariantType:
        """
        Determine the OPCUA data type for a given value.
        
        :param value: The value to determine the data type for
        :return: OPCUA Variant Type
        """

        if isinstance(value, bool):
            return ua.VariantType.Boolean
        elif isinstance(value, int):
            return ua.VariantType.Int64
        elif isinstance(value, float):
            return ua.VariantType.Double
        elif isinstance(value, str):
            return ua.VariantType.String
        elif isinstance(value, list):
            # For lists, use a more specific type if possible
            if all(isinstance(x, bool) for x in value):
                return ua.VariantType.Boolean
            elif all(isinstance(x, int) for x in value):
                return ua.VariantType.Int64
            elif all(isinstance(x, float) for x in value or isinstance(x, int) for x in value):
                return ua.VariantType.Double
            else:
                return ua.VariantType.Variant
        else:
            # Default to variant for complex types
            return ua.VariantType.Variant
        
    
    def stop_server(self):
        """
        Stop the OPCUA server.
        
        This method stops the update thread and shuts down the OPCUA server.
        """

        if not self._running:
            return
        
        #Stop the update thread
        self._stop_event.set()
        if self._update_thread:
            self._update_thread.join(timeout=2.0)
            self._update_thread = None
        
        #Stop the server
        if self._server:
            self._server.stop()
            self._server = None

        self._running = False
        self._nodes = {}
        self._property_values = {}

        self.log.info("OPCUA server stopped")

        @property
        def is_running(self) -> bool:
            """
            Check if the OPCUA server is running.
            
            :return: True if server running, False otherwise
            """

            return self._running
        
        def handle(self, cycle_delay: float = 0.1) -> None:
            """
            Handle OPCUA operations.
            
            This method is called periodically by Lewis. For OPCUA, most of the 
            handling is done by the server thread, so this method mainly waits.
            
            :param cycle_delay: Approximate time to spend handling requests
            """

            #Most handling is done by the OPCUA server itself
            if self._running and self.interface:
                time.sleep(min(cycle_delay, self._options.update_interval))

        def _update_variables(self) -> None:
            """
            Update OPCUA variables with current device values.
            
            This method runs in a separate thread and periodically updates the OPCUA
            variables with the current values from the device.
            """

            while not self._stop_event.is_set() and self._running and self.interface:
                #Update variables that have changed
                with self.device_lock:
                    for property, node in self._nodes.items():
                        if hasattr(self.interface, property):
                            current_value = getattr(self.interface, property)

                            #check if the value has changed
                            if property not in self._property_values or self._property_values[property] != current_value:
                                try:
                                    node.set_value(current_value)
                                    self._property_values[property] = current_value
                                except Exception as e:
                                    self.log.warning(f"Failed to update node {property}: {e}")
                    
                    self._stop_event.wait(self._options.update_interval)
        
