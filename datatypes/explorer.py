from typing import List
from typing import Optional, Dict

from pydantic import BaseModel, Field


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
    for_field: Optional[str] = Field(alias='for')


class ExplorerContent(BaseModel):
    dataType: str
    type: str
    hasPublicTransfer: bool
    fields: Optional[ExplorerContentMoveObject]


class ExplorerDataContent(BaseModel):
    data: ExplorerContent


class ExplorerCoinflipContent(BaseModel):
    pass


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
    fields: Optional[Dict]
    type: Optional[str]
    objectType: Optional[str]


class ExplorerBodyResult(BaseModel):
    data: ExplorerDataResult


class CoinContent(BaseModel):
    coinType: Optional[str]
    coinObjectId: Optional[str]
    balance: Optional[str]


class ExplorerResult(BaseModel):
    data: ExplorerDataResult | List[ExplorerBodyResult] | List[ExplorerDataResult]
    nextCursor: Optional[str]
    hasNextPage: Optional[bool]


class ExplorerSuiCoinsResult(BaseModel):
    data: List[CoinContent]
    nextCursor: Optional[str]
    hasNextPage: Optional[bool]


class ExplorerSuiCoinsResponse(BaseModel):
    result: ExplorerSuiCoinsResult


class ExplorerResponse(BaseModel):
    result: ExplorerResult


class Entry(BaseModel):
    bullsharkId: List[str]
    score: int
    numCommandsDeSuiFlip: int
    numCommandsEthos8192: int
    numCommandsJourneyToMountSogol: int
    numCommandsMiniMiners: int
    bot: bool


class Data(BaseModel):
    entry: Entry
    position: Optional[int]


class Result(BaseModel):
    data: Data | None


class PointRankResult(BaseModel):
    result: Result


class PointRankResponse(BaseModel):
    __root__: List[PointRankResult]
