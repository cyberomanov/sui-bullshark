import json

import requests
from loguru import logger

from data import SUI_MAINNET_RPC
from datatypes import ExplorerGetOwnedObjectsResponse, ExplorerBodyResult


def get_sui_owned_objects_response(address: str) -> ExplorerGetOwnedObjectsResponse:
    data = {
        "method": "suix_getOwnedObjects",
        "jsonrpc": "2.0",
        "params":
            [
                address,
                {
                    "options":
                        {
                            "showType": False,
                            "showOwner": False,
                            "showContent": True,
                            "showDisplay": True
                        }
                },
                None,
                None
            ],
        "id": "11"
    }
    response = requests.post(url=SUI_MAINNET_RPC, json=data)
    if response.status_code == 200:
        return ExplorerGetOwnedObjectsResponse.parse_obj(json.loads(response.content))
    else:
        logger.error(json.loads(response.content))


def get_owned_8192_objects(response: ExplorerGetOwnedObjectsResponse) -> list[ExplorerBodyResult]:
    owned_8192_objects = []

    for item in response.result.data:
        if item.data.display.data and item.data.display.data.name == "Sui 8192":
            owned_8192_objects.append(item)

    return owned_8192_objects


def get_active_game_8192_ids(games: list[ExplorerBodyResult]) -> list[str]:
    active_game_ids = []

    for item in games:
        content_fields = item.data.content.fields
        if not content_fields.game_over:
            active_game_ids.append(item.data.objectId)

    return active_game_ids


def get_game_items(address: str):
    return get_owned_8192_objects(response=get_sui_owned_objects_response(address=address))


def get_active_game_ids(address: str) -> list:
    return get_active_game_8192_ids(games=get_game_items(address=address))


def get_game_items_count(address: str) -> int:
    return len(get_game_items(address=address))
