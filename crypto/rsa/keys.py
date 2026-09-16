"""RSA key data structures and simple JSON serialization."""

from dataclasses import asdict, dataclass
import json
@dataclass(frozen=True)
class PublicKey:
    n: int
    e: int

    def __post_init__(self) -> None:
        if self.n <= 2 or self.e <= 1:
            raise ValueError("invalid RSA public key")

    def to_json(self) -> str:
        return json.dumps({"type": "RSA PUBLIC", **asdict(self)}, sort_keys=True)

    @classmethod
    def from_json(cls, value: str) -> "PublicKey":
        data = _load(value, "RSA PUBLIC", {"type", "n", "e"})
        return cls(n=data["n"], e=data["e"])


@dataclass(frozen=True)
class PrivateKey:
    n: int
    d: int
    p: int | None = None
    q: int | None = None

    def __post_init__(self) -> None:
        if self.n <= 2 or self.d <= 1:
            raise ValueError("invalid RSA private key")
        if (self.p is None) != (self.q is None):
            raise ValueError("p and q must either both be present or both be absent")
        if self.p is not None:
            assert self.q is not None
            if self.p * self.q != self.n:
                raise ValueError("p and q do not match n")

    def to_json(self, include_primes: bool = False) -> str:
        data: dict[str, int | str] = {"type": "RSA PRIVATE", "n": self.n, "d": self.d}
        if include_primes and self.p is not None:
            assert self.q is not None
            data.update(p=self.p, q=self.q)
        return json.dumps(data, sort_keys=True)

    @classmethod
    def from_json(cls, value: str) -> "PrivateKey":
        data = json.loads(value)
        if not isinstance(data, dict) or data.get("type") != "RSA PRIVATE":
            raise ValueError("invalid RSA private key serialization")
        if set(data) not in ({"type", "n", "d"}, {"type", "n", "d", "p", "q"}):
            raise ValueError("unexpected RSA private key fields")
        if not all(isinstance(data[field], int) for field in set(data) - {"type"}):
            raise ValueError("RSA key values must be integers")
        return cls(n=data["n"], d=data["d"], p=data.get("p"), q=data.get("q"))


def _load(value: str, expected_type: str, fields: set[str]) -> dict[str, int | str]:
    try:
        data = json.loads(value)
    except (TypeError, json.JSONDecodeError) as error:
        raise ValueError("invalid RSA key serialization") from error
    if not isinstance(data, dict) or data.get("type") != expected_type or set(data) != fields:
        raise ValueError("invalid RSA key serialization")
    if not isinstance(data["n"], int) or not isinstance(data["e"], int):
        raise ValueError("RSA key values must be integers")
    return data
