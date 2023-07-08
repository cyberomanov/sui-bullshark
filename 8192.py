import concurrent.futures
import random
import time

from loguru import logger
from pysui.sui.sui_config import SuiConfig

from config import total_max_8192_games_per_address, sleep_range_in_sec
from data import VERSION
from datatypes import Arrow
from utils import (add_logger,
                   read_mnemonics,
                   get_list_of_sui_configs,
                   execute_move,
                   mint_game,
                   short_address,
                   get_game_items_count,
                   get_active_game_ids)


def main_play_game(sui_config: SuiConfig, game_id: str):
    stop = False
    while not stop:
        try:
            result = execute_move(sui_config=sui_config, game_id=game_id, move=random.choice(list(Arrow)))
            if result.reason:
                logger.warning(f'{short_address(result.address)} | {result.move.name} | reason: {result.reason}.')
                stop = True
            else:
                logger.info(f'{short_address(result.address)} | {result.move.name} | digest: {result.digest}')
                time.sleep(random.randint(sleep_range_in_sec[0], sleep_range_in_sec[1]))
        except:
            pass


def main_mint_game(sui_config: SuiConfig):
    result = mint_game(sui_config=sui_config)
    if result.reason:
        logger.warning(f'{short_address(result.address)} | digest: {result.digest} | reason: {result.reason}.')
    else:
        logger.info(f'{short_address(result.address)} | digest: {result.digest}')


def single_executor(sui_config: SuiConfig):
    while get_game_items_count(address=str(sui_config.active_address)) < total_max_8192_games_per_address or \
            get_active_game_ids(address=str(sui_config.active_address)):

        active_game_8192_ids = get_active_game_ids(address=str(sui_config.active_address))

        if not active_game_8192_ids:
            main_mint_game(sui_config=sui_config)
            time.sleep(random.randint(sleep_range_in_sec[0], sleep_range_in_sec[1]))
            active_game_8192_ids = get_active_game_ids(address=str(sui_config.active_address))

        random_game = random.choice(active_game_8192_ids)
        logger.info(f'{short_address(str(sui_config.active_address))} | current_game_id: {random_game}.')
        main_play_game(sui_config=sui_config, game_id=random_game)
    logger.success(
        f'{short_address(str(sui_config.active_address))} | played {total_max_8192_games_per_address} games.')


def pool_executor(sui_configs: list[SuiConfig]):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(single_executor, sui_configs)


if __name__ == '__main__':
    add_logger(version=VERSION)
    try:
        mnemonics = read_mnemonics()
        sui_configs = get_list_of_sui_configs(mnemonics=mnemonics)

        logger.info('loaded addresses:')
        logger.info('-' * 66)

        for sui_config in sui_configs:
            logger.info(f'{sui_config.active_address}')

        logger.info('-' * 66)

        pool_executor(sui_configs=sui_configs)
    except Exception as e:
        logger.exception(e)
