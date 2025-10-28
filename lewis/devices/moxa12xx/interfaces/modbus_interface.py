from lewis.adapters.modbus import ModbusBasicDataBank, ModbusInterface
from lewis.core.logging import has_log


class GenericMoxa12XXInterface(ModbusInterface):
    """A generic interface which can be used to create a set of modbus registers for a device

    """

    @ModbusInterface.device.setter
    def device(self, new_device):
        """Overrides base implementation to give attached device a reference to self
        Required to allow communications between the interface and device
        """
        ModbusInterface.device.fset(self, new_device)
        self.device.interface = self


@has_log
class Moxa1210ModbusInterface(GenericMoxa12XXInterface):
    """Creates modbus data registers for a Moxa e1210 and makes them available to the lewis device.

    """

    protocol = "MOXA_1210"

    # Moxa 1210 has 16 (0x10) Discrete Input registers (di). The other register values are not tested.
    # The layout of these registers is described in Appendix A of the moxa e1200 series manual.

    di = ModbusBasicDataBank(False, last_addr=0x10)


@has_log
class Moxa1240ModbusInterface(GenericMoxa12XXInterface):
    """Creates modbus data registers for a Moxa e1240 and makes them available to the lewis device.

    """

    protocol = "MOXA_1240"

    # Moxa 1240 has 8 16-bit floats held in 8 (0x8) Input Registers (ir). The other register values are not tested.
    # The layout of these registers is described in Appendix A of the moxa e1200 series manual.

    ir = ModbusBasicDataBank(0, start_addr=0x0, last_addr=0x8)


@has_log
class Moxa1242ModbusInterface(GenericMoxa12XXInterface):
    """Creates modbus data registers for a Moxa e1242 and makes them available to the lewis device.

    """

    protocol = "MOXA_1242"

    # Moxa 1242 has 4 16-bit floats held in 4 (0x4) Input Registers (ir). The other register values are not tested.
    # The layout of these registers is described in Appendix A of the moxa e1200 series manual.

    ir = ModbusBasicDataBank(0, start_addr=0x200, last_addr=0x204)

    # Moxa 1242 has 8 (0x08) Discrete Input registers (di). The other register values are not tested.
    # The layout of these registers is described in Appendix A of the moxa e1200 series manual.

    di = ModbusBasicDataBank(False, last_addr=0x08)


@has_log
class Moxa1262ModbusInterface(GenericMoxa12XXInterface):
    """Creates modbus data registers for a Moxa e1240 and makes them available to the lewis device.

    """

    protocol = "MOXA_1262"

    # Moxa 1262 has 8 32-bit floats held in 16 (0x20) Input Registers (ir). The other register values are not tested.
    # The layout of these registers is described in Appendix A of the moxa e1200 series manual.

    ir = ModbusBasicDataBank(1, start_addr=0x810, last_addr=0x820)
