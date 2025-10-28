from lewis.adapters.stream import Cmd, StreamInterface
from lewis.core.logging import has_log
from lewis.utils.byte_conversions import raw_bytes_to_int

from ..device import SimulatedFinsPLC
from .response_utilities import check_is_byte, dm_memory_area_read_response_fins_frame


@has_log
class FinsPLCStreamInterface(StreamInterface):
    # Commands that we expect via serial during normal operation. Match anything!
    commands = {
        Cmd("any_command", r"^([\s\S]*)$", return_mapping=lambda x: x),
    }

    in_terminator = ""
    out_terminator = b""

    do_log = True

    def handle_error(self, request, error):
        error_message = (
            "An error occurred at request " + repr(request) + ": " + repr(error)
        )
        self.log.error(error_message)
        print(error_message)
        return str(error)

    def any_command(self, command):
        """Handles all command sent to this emulator. It checks the validity of the command, and raises an error if it
        finds something invalid. If the command is valid, then it returns a string representing the response to the
        command.

        Args:
            command (bytes): A string where every character represents a byte from the received FINS command frame.

        Returns:
            bytes: a string where each character represents a byte from the FINS response frame.
        """
        self._log_fins_frame(command, False)

        self._check_fins_frame_header_validity(command[:10])

        # We extract information necessary for building the FINS response header
        self.device.network_address = command[3]
        self.device.unit_address = command[5]

        client_network_address = command[6]
        client_node_address = command[7]
        client_unit_address = command[8]

        service_id = command[9]

        if command[10] != 0x01 or command[11] != 0x01:
            raise ValueError(
                "The command code should be 0x0101, for memory area read command!"
            )

        if command[12] != 0x82:
            raise ValueError(
                "The emulator only supports reading words from the DM area, for which the code is 82."
            )

        # the address of the starting word from where reading is done. Addresses are stored in two bytes.
        memory_start_address = raw_bytes_to_int(command[13:15], low_bytes_first=False)

        # The FINS PLC supports reading either a certain number of words, or can also read individual bits in a word.
        # The helium recovery memory map implies that that PLC uses word designated reading. When bit designated
        # reading is not used, the 16th byte of the command is 0x00.
        if command[15] != 0x00:
            raise ValueError(
                "The emulator only supports word designated memory reading. The bit address must "
                "be 0x00."
            )

        number_of_words_to_read = raw_bytes_to_int(
            command[16:18], low_bytes_first=False
        )

        # The helium recovery PLC memory map has addresses that store types that take up either one word (16 bits) or
        # two. Most take up one word, so if the number of words to read is two we check that the client wants to read
        # from a memory location from where a 32 bit value starts.
        if number_of_words_to_read == 2 and (
            memory_start_address not in self.device.int32_memory.keys()
            and memory_start_address not in self.device.float_memory.keys()
        ):
            raise ValueError(
                "The memory start address {} corresponds to a single word in the memory map, "
                "not two.".format(memory_start_address)
            )
        # The PLC also stores 32 bit floating point numbers, but the asyn device support makes the IOC ask for 4 bytes
        # instead of two.
        elif number_of_words_to_read > 2:
            raise ValueError(
                "The memory map only specifies data types for which commands should ask for one or two at most."
            )
        is_float = (
            True if memory_start_address in self.device.float_memory.keys() else False
        )
        self._log_command_contents(
            client_network_address,
            client_node_address,
            client_unit_address,
            service_id,
            memory_start_address,
            number_of_words_to_read,
        )

        reply = dm_memory_area_read_response_fins_frame(
            self.device,
            client_network_address,
            client_node_address,
            client_unit_address,
            service_id,
            memory_start_address,
            number_of_words_to_read,
            is_float,
        )

        self._log_fins_frame(reply, True)

        return reply

    def _log_fins_frame(self, fins_frame, is_reply):
        """Nicely displays every byte in the command as a hexadecimal number in the emulator log.

        Args:
            fins_frame (bytes): The fins frame we want to log.
            is_reply (bool): Whether we want to log the reply or the command.

        Returns:
            None.
        """
        if self.do_log:
            hex_command = [hex(character) for character in fins_frame]

            if not is_reply:
                self.log.info("command is {}".format(hex_command))
            else:
                self.log.info("reply is{}".format(hex_command))

    def _log_command_contents(
        self,
        client_network_address,
        client_node_address,
        client_unit_address,
        service_id,
        memory_start_address,
        number_of_words_to_read,
    ):
        """Nicely displays the bits of information in the FINS command that will be used for building the reply as numbers.

        Args:
            client_network_address (int): The FINS network address of the client.
            client_node_address (int): The FINS node of the client.
            client_unit_address (int): The FINS unit address of the client.
            service_id (int): The service ID of the original command.
            memory_start_address (int): The memory address from where reading starts.
            number_of_words_to_read (int): The number of words to be read, starting from the start address, inclusive.

        Returns:
            None.
        """
        if self.do_log:
            self.log.info(
                "Server network address: {}".format(self.device.network_address)
            )
            self.log.info("Server Unit address: {}".format(self.device.unit_address))
            self.log.info("Client network address: {}".format(client_network_address))
            self.log.info("Client node address: {}".format(client_node_address))
            self.log.info("Client unit address: {}".format(client_unit_address))
            self.log.info("Service id: {}".format(service_id))
            self.log.info("Memory start address: {}".format(memory_start_address))
            self.log.info("Number of words to read: {}".format(number_of_words_to_read))

    @staticmethod
    def _check_fins_frame_header_validity(fins_frame_header):
        """Checks that the FINS frame header part of the command is valid for a command sent from a client to a server
        (PLC).

        Args:
            fins_frame_header (bytes): A string where every character represents a byte from the received FINS frame
                header.

        Returns:
            None.
        """
        # ICF means Information Control Field, it gives information about if the frame is for a command or a response,
        # and if a response is needed or not.
        icf = fins_frame_header[0]
        if icf != 0x80:
            raise ValueError(
                "ICF value should always be 0x80 for a command sent to the emulator"
            )

        # Reserved byte. Should always be 0x00
        if fins_frame_header[1] != 0x00:
            raise ValueError("Reserved byte should always be 0x00.")

        if fins_frame_header[2] != 0x02:
            raise ValueError("Gate count should always be 0x02.")

        check_is_byte(fins_frame_header[3])

        if fins_frame_header[4] != SimulatedFinsPLC.HELIUM_RECOVERY_NODE:
            raise ValueError(
                "The node address of the FINS helium recovery PLC should be {}!".format(
                    SimulatedFinsPLC.HELIUM_RECOVERY_NODE
                )
            )

        for i in range(5, 10):
            check_is_byte(fins_frame_header[i])
