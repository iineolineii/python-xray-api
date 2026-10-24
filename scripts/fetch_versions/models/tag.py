from dataclasses import dataclass
from datetime import datetime


@dataclass
class Tag:
    name: str
    date: datetime


__all__ = ["Tag"]
