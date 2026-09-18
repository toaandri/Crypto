"""Textbook RSA signatures: deliberately without PSS padding."""

from .rsa import sign, verify

__all__ = ["sign", "verify"]
