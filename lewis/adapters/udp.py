"""
UDP adapter. Each datagram is one request, matched against the interface's ``commands``
in the same way as :class:`~lewis.adapters.stream.StreamInterface`.
"""

import asyncio

from lewis.adapters.stream import StreamInterface
from lewis.core.adapters import Adapter


class UDPAdapter(Adapter, asyncio.DatagramProtocol):
    """
    Available options are:

     - bind_address: IP to bind on (defaults to 0.0.0.0)
     - port: Port to listen on (defaults to 9999)
    """

    default_options = {"bind_address": "0.0.0.0", "port": 9999}  # ruff: ignore [RUF012]

    def __init__(self, options=None) -> None:
        super().__init__(options)
        self._transport = None

    async def start_server(self) -> None:
        self._transport, _ = await asyncio.get_running_loop().create_datagram_endpoint(
            lambda: self, local_addr=(self._options.bind_address, self._options.port)
        )

    async def stop_server(self) -> None:
        if self._transport is not None:
            self._transport.close()
            self._transport = None

    @property
    def is_running(self) -> bool:
        return self._transport is not None

    async def handle(self, cycle_delay=0.1) -> None:
        await asyncio.sleep(cycle_delay)

    def datagram_received(self, data, addr) -> None:
        with self.device_lock:
            try:
                cmd = next(c for c in self.interface.bound_commands if c.can_process(data))
                reply = cmd.process_request(data)
            except StopIteration:
                reply = self.interface.handle_error(data, RuntimeError("No command matched."))
            except Exception as error:  # ruff: ignore [BLE001]
                reply = self.interface.handle_error(data, error)

        if reply is not None:
            self._transport.sendto(reply.encode() if isinstance(reply, str) else reply, addr)


class UDPInterface(StreamInterface):
    """
    This class is used to provide a UDP based interface for a device which responds to commands.

    It does not currently handle sending unsolicited traffic - it just responds to datagrams which are received.
    Commands returning ``None`` send no reply.
    """

    protocol = "udp"

    @property
    def adapter(self):
        return UDPAdapter
