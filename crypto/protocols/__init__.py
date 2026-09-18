"""In-memory authenticated communication simulation."""

from .secure_channel import Handshake, Hello, Packet, SecureChannel, establish_channels

__all__ = ["Handshake", "Hello", "Packet", "SecureChannel", "establish_channels"]
