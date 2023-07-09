from typing import List
from typing import Optional

from pydantic import BaseModel


class ExplorerGameId(BaseModel):
    id: str


class ExplorerGameBoard8192(BaseModel):
    game_over: Optional[bool]
    last_tile: Optional[List[str]]
    packed_spaces: Optional[str]
    score: Optional[str]
    top_tile: Optional[str]


class ExplorerContentMoveObject(BaseModel):
    active_board: Optional[ExplorerGameBoard8192]
    game: Optional[str]
    game_over: Optional[bool]
    id: Optional[ExplorerGameId]
    move_count: Optional[str]
    player: Optional[str]
    score: Optional[str]
    top_tile: Optional[str]


class ExplorerContent(BaseModel):
    dataType: str
    type: str
    hasPublicTransfer: bool
    fields: Optional[ExplorerContentMoveObject]


class ExplorerDataContent(BaseModel):
    data: ExplorerContent


class ExplorerDataDisplay(BaseModel):
    creator: Optional[str]
    description: Optional[str]
    game: Optional[str]
    image_url: Optional[str]
    name: Optional[str]
    project_image_url: Optional[str]
    project_name: Optional[str]
    project_url: Optional[str]
    link: Optional[str]


class ExplorerBodyDisplay(BaseModel):
    data: Optional[ExplorerDataDisplay]


class ExplorerDataResult(BaseModel):
    objectId: Optional[str]
    version: Optional[str]
    digest: Optional[str]
    display: Optional[ExplorerBodyDisplay]
    content: Optional[ExplorerContent]


class ExplorerBodyResult(BaseModel):
    data: ExplorerDataResult


class ExplorerResult(BaseModel):
    data: List[ExplorerBodyResult] | ExplorerDataResult
    nextCursor: Optional[str]
    hasNextPage: Optional[bool]


class ExplorerResponse(BaseModel):
    result: ExplorerResult



