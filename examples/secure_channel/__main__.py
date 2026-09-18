from dataclasses import replace

from crypto.protocols import establish_channels


def main():
    alice, bob = establish_channels(b"pre-shared-demo-key-at-least-16-bytes")
    packet = alice.send("Bonjour Bob !".encode())
    altered = replace(packet, ciphertext=bytes([packet.ciphertext[0] ^ 1]) + packet.ciphertext[1:])
    try:
        bob.receive(altered)
    except ValueError:
        print("Alteration detectee avant dechiffrement.")
    print("Bob recoit :", bob.receive(packet).decode())
    print("Alice recoit :", alice.receive(bob.send(b"Bonjour Alice !")).decode())
    try:
        bob.receive(packet)
    except ValueError:
        print("Rejeu detecte.")


if __name__ == "__main__":
    main()
