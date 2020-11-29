import struct

from adafruit_bluefruit_connect.packet import Packet

class BrightnessPacket(Packet):
    """A packet containing a brightness value."""

    _FMT_PARSE = "<xxBx"
    PACKET_LENGTH = struct.calcsize(_FMT_PARSE)
    # _FMT_CONSTRUCT doesn't include the trailing checksum byte.
    _FMT_CONSTRUCT = "<2sB"
    _TYPE_HEADER = b"!B"

    def __init__(self, brightness):
        """Construct a BrightnessPacket from a 1-tuple of a value between 0 and 100,
        :param tuple/int color: an RGB tuple ``(brightness,)``
        """
        if isinstance(brightness, int):
            self._brightness = brightness.to_bytes("B", "big")
        elif len(brightness) == 1 and 0 <= brightness[0] <= 100:
            self._brightness = brightness[0]
        else:
            raise ValueError("Brightness must be a tuple(r,)")

    @classmethod
    def parse_private(cls, packet):
        """Construct a BrightnessPacket from an incoming packet.
        Do not call this directly; call Packet.from_bytes() instead.
        pylint makes it difficult to call this method _parse(), hence the name.
        """
        return cls(struct.unpack(cls._FMT_PARSE, packet))

    def to_bytes(self):
        """Return the bytes needed to send this packet.
        """
        partial_packet = struct.pack(
            self._FMT_CONSTRUCT, self._TYPE_HEADER, *self._brightness
        )
        return self.add_checksum(partial_packet)

    @property
    def brightness(self):
        """A tuple(red, green blue)."""
        return self._brightness

class SettingsRequestPacket(Packet):
    """A packet containing a brightness value."""

    _FMT_PARSE = "<xxx"
    PACKET_LENGTH = struct.calcsize(_FMT_PARSE)
    # _FMT_CONSTRUCT doesn't include the trailing checksum byte.
    _FMT_CONSTRUCT = "<2s"
    _TYPE_HEADER = b"!S"

    # def __init__(self, brightness):
    #     """Construct a BrightnessPacket from a 1-tuple of a value between 0 and 100,
    #     :param tuple/int color: an RGB tuple ``(brightness,)``
    #     """
    #     if isinstance(brightness, int):
    #         self._brightness = brightness.to_bytes("B", "big")
    #     elif len(brightness) == 1 and 0 <= brightness[0] <= 100:
    #         self._brightness = brightness[0]
    #     else:
    #         raise ValueError("Brightness must be a tuple(r,)")

    @classmethod
    def parse_private(cls, packet):
        """Construct a BrightnessPacket from an incoming packet.
        Do not call this directly; call Packet.from_bytes() instead.
        pylint makes it difficult to call this method _parse(), hence the name.
        """
        return cls(struct.unpack(cls._FMT_PARSE, packet))

    # def to_bytes(self):
    #     """Return the bytes needed to send this packet.
    #     """
    #     partial_packet = struct.pack(
    #         self._FMT_CONSTRUCT, self._TYPE_HEADER, *self._brightness
    #     )
    #     return self.add_checksum(partial_packet)

    # @property
    # def brightness(self):
    #     """A tuple(red, green blue)."""
    #     return self._brightness

# Register this class with the superclass. This allows the user to import only what is needed.
BrightnessPacket.register_packet_type()
SettingsRequestPacket.register_packet_type()