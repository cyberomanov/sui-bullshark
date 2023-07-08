from enum import Enum
from typing import Optional

from pydantic import BaseModel


class Arrow(Enum):
    LEFT = 3
    UP = 2
    DOWN = 1
    RIGHT = 0


class Sui8192TransactionResult(BaseModel):
    address: str
    digest: str


class Sui8192MoveResult(Sui8192TransactionResult):
    move: Arrow
    reason: Optional[str]


class Sui8192CreateResult(Sui8192TransactionResult):
    reason: Optional[str]
