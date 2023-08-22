import concurrent.futures
import random
import time

from loguru import logger
from pysui.sui.sui_config import SuiConfig

from config import (short_sleep_between_txs_in_range_in_sec, start_threads_simultaneously,
                    navi_liquidity_value_in_sui_in_range,
                    long_sleep_between_txs_in_range_in_sec)
from utils import (short_address,
                   get_sui_balance, navi_deposit_sui_tx, navi_borrow_sui_tx, navi_repay_sui_tx)
from utils.other_tools import get_sui_balance_object_from_range


def main_navi_deposit_borrow_repay_sui(sui_config: SuiConfig):
    try:
        amount_to_provide = get_sui_balance_object_from_range(min_amount=navi_liquidity_value_in_sui_in_range[0],
                                                              max_amount=navi_liquidity_value_in_sui_in_range[1],
                                                              num_of_zero_after_decimal_point=4)

        balance = get_sui_balance(sui_config=sui_config)
        if balance.int > int(amount_to_provide.int * 1.01):
            result = navi_deposit_sui_tx(sui_config=sui_config, amount=amount_to_provide)
            sleep = 0
            if result.reason:
                if result.digest:
                    sleep = random.randint(short_sleep_between_txs_in_range_in_sec[0],
                                           short_sleep_between_txs_in_range_in_sec[1])
                    logger.error(
                        f'{short_address(result.address)} | NAVI_DEPOSIT | {amount_to_provide.float} $SUI | '
                        f'digest: {result.digest} | '
                        f'reason: {result.reason} | sleep: {sleep}s.')
                else:
                    logger.error(
                        f'{short_address(result.address)} | NAVI_DEPOSIT | {amount_to_provide.float} $SUI | '
                        f'reason: {result.reason} | sleep: {sleep}s.')
            else:
                sleep = random.randint(short_sleep_between_txs_in_range_in_sec[0],
                                       short_sleep_between_txs_in_range_in_sec[1])
                logger.info(f'{short_address(result.address)} | NAVI_DEPOSIT | {amount_to_provide.float} $SUI | '
                            f'digest: {result.digest} | '
                            f'sleep: {sleep}s.')

            time.sleep(sleep)

            amount_to_borrow = get_sui_balance_object_from_range(min_amount=amount_to_provide.float * 0.3,
                                                                 max_amount=amount_to_provide.float * 0.4,
                                                                 num_of_zero_after_decimal_point=4)

            result = navi_borrow_sui_tx(sui_config=sui_config, amount=amount_to_borrow)
            sleep = 0
            if result.reason:
                if result.digest:
                    sleep = random.randint(short_sleep_between_txs_in_range_in_sec[0],
                                           short_sleep_between_txs_in_range_in_sec[1])
                    logger.error(
                        f'{short_address(result.address)} | NAVI_BORROW | {amount_to_borrow.float} $SUI | '
                        f'digest: {result.digest} | '
                        f'reason: {result.reason} | sleep: {sleep}s.')
                else:
                    logger.error(
                        f'{short_address(result.address)} | NAVI_BORROW | {amount_to_borrow.float} $SUI | '
                        f'reason: {result.reason} | sleep: {sleep}s.')
            else:
                sleep = random.randint(long_sleep_between_txs_in_range_in_sec[0],
                                       long_sleep_between_txs_in_range_in_sec[1])
                logger.info(f'{short_address(result.address)} | NAVI_BORROW | {amount_to_borrow.float} $SUI | '
                            f'digest: {result.digest} | '
                            f'sleep: {sleep}s.')

            time.sleep(sleep)

            result = navi_repay_sui_tx(sui_config=sui_config, amount=amount_to_borrow)
            sleep = 0
            if result.reason:
                if result.digest:
                    sleep = random.randint(short_sleep_between_txs_in_range_in_sec[0],
                                           short_sleep_between_txs_in_range_in_sec[1])
                    logger.error(
                        f'{short_address(result.address)} | NAVI_REPAY | {amount_to_borrow.float} $SUI | '
                        f'digest: {result.digest} | '
                        f'reason: {result.reason} | sleep: {sleep}s.')
                else:
                    logger.error(
                        f'{short_address(result.address)} | NAVI_REPAY | {amount_to_borrow.float} $SUI | '
                        f'reason: {result.reason} | sleep: {sleep}s.')
            else:
                sleep = random.randint(short_sleep_between_txs_in_range_in_sec[0],
                                       short_sleep_between_txs_in_range_in_sec[1])
                logger.info(f'{short_address(result.address)} | NAVI_REPAY | {amount_to_borrow.float} $SUI | '
                            f'digest: {result.digest} | '
                            f'sleep: {sleep}s.')

            time.sleep(sleep)
        else:
            logger.warning(f'{short_address(str(sui_config.active_address))} | NAVI_DEPOSIT | '
                           f'balance is not enough: {balance.float} $SUI. '
                           f'minimum required: {round(amount_to_provide.int * 1.01, 2)} $SUI.')

    except Exception as e:
        logger.exception(e)


def single_executor(sui_config: SuiConfig):
    if not start_threads_simultaneously:
        time.sleep(random.randint(1, 60))

    # merge_sui_coins(sui_config=sui_config)
    main_navi_deposit_borrow_repay_sui(sui_config=sui_config)


def main_navi_executor(sui_configs: list[SuiConfig]):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(single_executor, sui_configs)
