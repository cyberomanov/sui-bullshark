import json
import random
import time

import requests
from loguru import logger
from pysui import SuiConfig

from config import sui_rpc
from datatypes import (ExplorerResponse,
                       ExplorerBodyResult,
                       ExplorerSuiCoinsResponse,
                       PointRankResponse,
                       PointRankResult)
from utils.sui import get_sui_balance


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
            response = requests.post(url=sui_rpc, json=data)
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
    response = requests.post(url=sui_rpc, json=data)
    if response.status_code == 200:
        return ExplorerResponse.parse_obj(json.loads(response.content))
    else:
        logger.error(json.loads(response.content))


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


def get_associated_kiosk(address: str) -> str:
    response = get_sui_owned_objects_response(address=address)

    for item in response.result.data:
        if item.data.content.fields.for_field:
            return item.data.content.fields.for_field


def get_bullshark_id(kiosk_addr: str):
    data = {
        "method": "suix_getDynamicFields",
        "jsonrpc": "2.0",
        "params": [kiosk_addr],
        "id": "1"
    }
    response = requests.post(url=sui_rpc, json=data)
    if response.status_code == 200:
        return ExplorerResponse.parse_obj(json.loads(response.content))
    else:
        logger.error(json.loads(response.content))


def get_sui_coin_objects(address: str):
    data = {
        "method": "suix_getCoins",
        "jsonrpc": "2.0",
        "params": [address, "0x2::sui::SUI"],
        "id": "14"
    }
    response = requests.post(url=sui_rpc, json=data)
    if response.status_code == 200:
        return ExplorerSuiCoinsResponse.parse_obj(json.loads(response.content))
    else:
        logger.error(json.loads(response.content))


def get_points_and_rank(address: str):
    url = f"https://quests.mystenlabs.com/api/trpc/user?" \
          f"batch=1&" \
          f"input=%7B%220%22%3A%7B%22address%22%3A%22{address}%22%7D%7D"

    try:
        response = requests.get(url=url)
        if response.status_code == 200:
            return PointRankResponse.parse_obj(json.loads(response.content))
        else:
            logger.error(json.loads(response.content))
    except Exception as e:
        logger.exception(e)


def print_rank_and_balance(sui_config: SuiConfig):
    rank: PointRankResult = get_points_and_rank(address=str(sui_config.active_address)).__root__[0]
    rank_data = rank.result.data
    if not rank_data.entry.suspectedBot:
        if rank_data.position:
            if rank_data.position < 10_000:
                logger.success(
                    f'{sui_config.active_address}: {get_sui_balance(sui_config=sui_config).float} $SUI | '
                    f'coinflip: {rank_data.entry.numCommandsDeSuiFlip}, '
                    f'8192: {rank_data.entry.numCommandsEthos8192}, '
                    f'miners: {rank_data.entry.numCommandsMiniMiners}, '
                    f'journey: {rank_data.entry.numCommandsJourneyToMountSogol} | '
                    f'#{rank_data.position}, score: {rank_data.entry.score}.')
            else:
                logger.info(
                    f'{sui_config.active_address}: {get_sui_balance(sui_config=sui_config).float} $SUI | '
                    f'coinflip: {rank_data.entry.numCommandsDeSuiFlip}, '
                    f'8192: {rank_data.entry.numCommandsEthos8192}, '
                    f'miners: {rank_data.entry.numCommandsMiniMiners}, '
                    f'journey: {rank_data.entry.numCommandsJourneyToMountSogol} | '
                    f'#{rank_data.position}, score: {rank_data.entry.score}.')
        else:
            logger.warning(f'{sui_config.active_address}: {get_sui_balance(sui_config=sui_config).float} $SUI | '
                           f'coinflip: {rank_data.entry.numCommandsDeSuiFlip}, '
                           f'8192: {rank_data.entry.numCommandsEthos8192}, '
                           f'miners: {rank_data.entry.numCommandsMiniMiners}, '
                           f'journey: {rank_data.entry.numCommandsJourneyToMountSogol} | '
                           f'score: {rank_data.entry.score}.')
    else:
        logger.warning(f'{sui_config.active_address}: {get_sui_balance(sui_config=sui_config).float} $SUI | '
                       f'coinflip: {rank_data.entry.numCommandsDeSuiFlip}, '
                       f'8192: {rank_data.entry.numCommandsEthos8192}, '
                       f'miners: {rank_data.entry.numCommandsMiniMiners}, '
                       f'journey: {rank_data.entry.numCommandsJourneyToMountSogol} | '
                       f'score: {rank_data.entry.score} | BOT.')
