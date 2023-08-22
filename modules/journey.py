import concurrent.futures
import random
import time

from loguru import logger
from pysui.sui.sui_clients.sync_client import SuiClient
from pysui.sui.sui_config import SuiConfig

from config import (short_sleep_between_txs_in_range_in_sec, start_threads_simultaneously)
from data import GAME_JOURNEY_MAIN_ADDRESS
from utils import (short_address,
                   merge_sui_coins,
                   create_profile,
                   save_quest_tx,
                   get_sui_balance)
from utils.other_tools import get_random_username


def main_create_profile(sui_config: SuiConfig, nickname: str, img_url: str = '', description: str = ''):
    try:
        result = create_profile(sui_config=sui_config,
                                nickname=nickname,
                                img_url=img_url,
                                description=description)

        sleep = 0
        if result.reason:
            if result.digest:
                sleep = random.randint(short_sleep_between_txs_in_range_in_sec[0],
                                       short_sleep_between_txs_in_range_in_sec[1])
                logger.error(
                    f'{short_address(result.address)} | create_profile | digest: {result.digest} | '
                    f'reason: {result.reason} | sleep: {sleep}s.')
            else:
                logger.error(
                    f'{short_address(result.address)} | create_profile | '
                    f'reason: {result.reason}.')
        else:
            sleep = random.randint(short_sleep_between_txs_in_range_in_sec[0],
                                   short_sleep_between_txs_in_range_in_sec[1])
            logger.info(f'{short_address(result.address)} | create_profile | digest: {result.digest} | '
                        f'sleep: {sleep}s.')

        time.sleep(sleep)
    except Exception as e:
        logger.exception(e)


def main_save_quest(sui_config: SuiConfig, profile_addr: str):
    try:
        result = save_quest_tx(sui_config=sui_config, profile_addr=profile_addr)

        sleep = 0
        if result.reason:
            if result.digest:
                sleep = random.randint(short_sleep_between_txs_in_range_in_sec[0],
                                       short_sleep_between_txs_in_range_in_sec[1])
                logger.error(
                    f'{short_address(result.address)} | save_quest | digest: {result.digest} | '
                    f'reason: {result.reason} | sleep: {sleep}s.')
            else:
                if 'dynamic_field::add' not in result.reason:
                    logger.error(
                        f'{short_address(result.address)} | save_quest | '
                        f'reason: {result.reason}.')
                else:
                    logger.info(
                        f'{short_address(result.address)} | quest is already saved.')
        else:
            sleep = random.randint(short_sleep_between_txs_in_range_in_sec[0],
                                   short_sleep_between_txs_in_range_in_sec[1])
            logger.info(f'{short_address(result.address)} | save_quest | digest: {result.digest} | '
                        f'sleep: {sleep}s.')

        time.sleep(sleep)
    except Exception as e:
        logger.exception(e)


def single_executor(sui_config: SuiConfig):
    if not start_threads_simultaneously:
        time.sleep(random.randint(1, 60))

    merge_sui_coins(sui_config=sui_config)

    client = SuiClient(config=sui_config)
    if get_sui_balance(sui_config=sui_config).int:
        profile_objects = [item for item in list(client.get_objects().result_data.data) if
                           item.object_type == f'{GAME_JOURNEY_MAIN_ADDRESS}::profile::Profile']

        if not len(profile_objects):
            main_create_profile(sui_config=sui_config, nickname=get_random_username(), img_url='', description='')
            profile_objects = [item for item in list(client.get_objects().result_data.data) if
                               item.object_type == f'{GAME_JOURNEY_MAIN_ADDRESS}::profile::Profile']
        else:
            logger.info(f'{short_address(str(sui_config.active_address))} | profile is already created.')

        if profile_objects:
            main_save_quest(sui_config=sui_config, profile_addr=profile_objects[0].object_id)
    else:
        logger.warning(f'{short_address(str(sui_config.active_address))} | zero_balance.')


def main_journey_executor(sui_configs: list[SuiConfig]):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(single_executor, sui_configs)
