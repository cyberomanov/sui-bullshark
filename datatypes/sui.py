from enum import Enum
from typing import Optional

from pydantic import BaseModel


class Arrow(Enum):
    RIGHT = 0
    DOWN = 1
    UP = 2
    LEFT = 3


class Sui8192TransactionResult(BaseModel):
    address: str
    digest: str


class Sui8192MoveResult(Sui8192TransactionResult):
    move: Arrow
    reason: Optional[str]


class Sui8192CreateResult(Sui8192TransactionResult):
    reason: Optional[str]
