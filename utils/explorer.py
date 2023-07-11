import json
import random
import time

import requests
from loguru import logger

from data import SUI_MAINNET_RPC
from datatypes import ExplorerResponse, ExplorerBodyResult


def get_sui_owned_objects_response(address: str) -> ExplorerResponse:
    has_next_page = True
    next_cursor = None
    limit = 50

    explorer_response = None

    while has_next_page:
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
                    next_cursor,
                    limit
                ],
            "id": "11"
        }
        try:
            response = requests.post(url=SUI_MAINNET_RPC, json=data)
            if response.status_code == 200:
                latest_response = ExplorerResponse.parse_obj(json.loads(response.content))
                has_next_page = latest_response.result.hasNextPage
                next_cursor = latest_response.result.nextCursor

                if explorer_response:
                    explorer_response.result.data += latest_response.result.data
                    time.sleep(random.randint(3, 5))
                else:
                    explorer_response = latest_response
            else:
                logger.error(json.loads(response.content))
        except Exception as e:
            logger.exception(e)

    return explorer_response


def get_owned_8192_objects(response: ExplorerResponse) -> list[ExplorerBodyResult]:
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


def get_sui_object_response(object_id: str) -> ExplorerResponse:
    data = {
        "method": "sui_getObject",
        "jsonrpc": "2.0",
        "params":
            [
                object_id,
                {
                    "showType": True,
                    "showContent": True,
                    "showOwner": True,
                    "showPreviousTransaction": True,
                    "showStorageRebate": True,
                    "showDisplay": True
                },
            ],
        "id": "2"
    }
    response = requests.post(url=SUI_MAINNET_RPC, json=data)
    if response.status_code == 200:
        return ExplorerResponse.parse_obj(json.loads(response.content))
    else:
        logger.error(json.loads(response.content))
