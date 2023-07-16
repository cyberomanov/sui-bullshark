import concurrent.futures
import random
import time

from loguru import logger
from pysui.sui.sui_config import SuiConfig

from config import max_flip_count_per_session_in_range, flip_bet_variants_in_sui, sleep_range_between_games_in_sec
from data import VERSION
from datatypes import CoinflipSide
from utils import (add_logger,
                   read_mnemonics,
                   get_list_of_sui_configs,
                   short_address,
                   play_coinflip_tx,
                   get_associated_kiosk,
                   get_bullshark_id,
                   merge_sui_coins)


def main_play_game(sui_config: SuiConfig, associated_kiosk_addr: str, bullshark_addr: str):
    try:
        coinflip_side = random.choice(list(CoinflipSide))
        bet_amount = random.choice(flip_bet_variants_in_sui)

        result = play_coinflip_tx(sui_config=sui_config,
                                  associated_kiosk_addr=associated_kiosk_addr,
                                  bullshark_addr=bullshark_addr,
                                  coinflip_side=coinflip_side,
                                  bet_amount=bet_amount)
        if result.reason:
            if result.digest:
                logger.warning(f'{short_address(result.address)} | {coinflip_side.name} | digest: {result.digest} | '
                               f'reason: {result.reason}.')
                return True
        else:
            logger.info(f'{short_address(result.address)} | {coinflip_side.name} | digest: {result.digest}')
            return True
    except Exception as e:
        logger.exception(e)


def single_executor(sui_config: SuiConfig):
    associated_kiosk_addr = get_associated_kiosk(address=str(sui_config.active_address))
    bullshark_addr = get_bullshark_id(kiosk_addr=associated_kiosk_addr).result.data[0].objectId

    flips_per_session = random.randint(max_flip_count_per_session_in_range[0], max_flip_count_per_session_in_range[1])
    for _ in range(flips_per_session):
        merge_sui_coins(sui_config=sui_config)
        game_result = main_play_game(sui_config=sui_config,
                                     associated_kiosk_addr=associated_kiosk_addr,
                                     bullshark_addr=bullshark_addr)
        if game_result:
            sleep = random.randint(sleep_range_between_games_in_sec[0], sleep_range_between_games_in_sec[1])
            logger.info(f'{short_address(str(sui_config.active_address))} | sleep: {sleep}s.')
            time.sleep(sleep)

    logger.success(f'{short_address(str(sui_config.active_address))} | has played {flips_per_session} games.')


def pool_executor(sui_configs: list[SuiConfig]):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(single_executor, sui_configs)


if __name__ == '__main__':
    add_logger(version=VERSION)
    try:
        mnemonics = read_mnemonics()
        sui_configs = get_list_of_sui_configs(mnemonics=mnemonics)

        logger.info('loaded addresses for coinflip game:')
        logger.info('-' * 66)

        for sui_config in sui_configs:
            logger.info(f'{sui_config.active_address}')

        logger.info('-' * 66)

        pool_executor(sui_configs=sui_configs)
    except Exception as e:
        logger.exception(e)
    except KeyboardInterrupt:
        exit()
