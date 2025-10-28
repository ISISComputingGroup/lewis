from lewis_emulators.tti355.interfaces.stream_interface import Tti355StreamInterface

__all__ = ["Ttiex355pStreamInterface"]


class Ttiex355pStreamInterface(Tti355StreamInterface):
    protocol = "ttiex355p"
