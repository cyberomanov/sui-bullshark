import concurrent.futures
import random
import time

from loguru import logger
from pysui.sui.sui_config import SuiConfig

from config import (short_sleep_between_txs_in_range_in_sec,
                    start_threads_simultaneously)
from data import CAPY_MINT_PRICE
from utils import (short_address,
                   get_sui_balance,
                   capy_mint_sui_tx)


def main_minter(sui_config: SuiConfig):
    try:
        balance = get_sui_balance(sui_config=sui_config)
        if balance.int > CAPY_MINT_PRICE:
            result = capy_mint_sui_tx(sui_config=sui_config)
            sleep = 0
            if result.reason:
                if result.digest:
                    sleep = random.randint(short_sleep_between_txs_in_range_in_sec[0],
                                           short_sleep_between_txs_in_range_in_sec[1])
                    logger.error(
                        f'{short_address(result.address)} | CAPY_MINTER | digest: {result.digest} | '
                        f'reason: {result.reason} | sleep: {sleep}s.')
                else:
                    logger.error(
                        f'{short_address(result.address)} | CAPY_MINTER | '
                        f'reason: {result.reason} | sleep: {sleep}s.')
            else:
                sleep = random.randint(short_sleep_between_txs_in_range_in_sec[0],
                                       short_sleep_between_txs_in_range_in_sec[1])
                logger.info(f'{short_address(result.address)} | CAPY_MINTER | digest: {result.digest} | '
                            f'sleep: {sleep}s.')
            time.sleep(sleep)

    except Exception as e:
        logger.exception(e)


def single_executor(sui_config: SuiConfig):
    if not start_threads_simultaneously:
        time.sleep(random.randint(1, 60))

    # merge_sui_coins(sui_config=sui_config)
    main_minter(sui_config=sui_config)


def main_minter_executor(sui_configs: list[SuiConfig]):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(single_executor, sui_configs)
