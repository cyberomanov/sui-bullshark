import concurrent.futures
import itertools
import random
import time

from loguru import logger
from pysui.sui.sui_clients.sync_client import SuiClient
from pysui.sui.sui_config import SuiConfig
from pysui.sui.sui_txresults import SuiCoinObjects
from pysui.sui.sui_types import SuiString

from config import (short_sleep_between_txs_in_range_in_sec,
                    start_threads_simultaneously,
                    scallop_liquidity_value_in_sui_in_range)
from data import SUI_RESERVE_COIN_TYPE, SUI_DENOMINATION
from utils import (short_address,
                   get_sui_balance,
                   scallop_deposit_sui_tx,
                   scallop_withdraw_sui_tx,
                   get_provided_sui_balance)
from utils.other_tools import get_sui_balance_object_from_range


def main_scallop_deposit_sui(sui_config: SuiConfig):
    try:
        provided_sui = get_provided_sui_balance(sui_config=sui_config)
        if provided_sui.int < int(scallop_liquidity_value_in_sui_in_range[0] * 10 ** SUI_DENOMINATION):
            amount_to_provide = get_sui_balance_object_from_range(
                min_amount=scallop_liquidity_value_in_sui_in_range[0],
                max_amount=scallop_liquidity_value_in_sui_in_range[1]
            )

            difference = amount_to_provide.int - provided_sui.int
            if difference > get_sui_balance_object_from_range(min_amount=0.001, max_amount=0.002).int:

                amount_to_provide = get_sui_balance_object_from_range(
                    min_amount=round(difference * 1 / 10 ** SUI_DENOMINATION, 2),
                    max_amount=round(difference * 1 / 10 ** SUI_DENOMINATION, 2)
                )

                balance = get_sui_balance(sui_config=sui_config)
                if balance.int > int(amount_to_provide.int * 1.1):
                    result = scallop_deposit_sui_tx(sui_config=sui_config, amount=amount_to_provide)

                    sleep = 0
                    if result.reason:
                        if result.digest:
                            sleep = random.randint(short_sleep_between_txs_in_range_in_sec[0],
                                                   short_sleep_between_txs_in_range_in_sec[1])
                            logger.error(
                                f'{short_address(result.address)} | SCALLOP_DEPOSIT | {amount_to_provide.float} $SUI | '
                                f'digest: {result.digest} | reason: {result.reason} | sleep: {sleep}s.')
                        else:
                            logger.error(
                                f'{short_address(result.address)} | SCALLOP_DEPOSIT | {amount_to_provide.float} $SUI | '
                                f'reason: {result.reason} | sleep: {sleep}s.')
                    else:
                        sleep = random.randint(short_sleep_between_txs_in_range_in_sec[0],
                                               short_sleep_between_txs_in_range_in_sec[1])
                        logger.info(
                            f'{short_address(result.address)} | SCALLOP_DEPOSIT | {amount_to_provide.float} $SUI | '
                            f'digest: {result.digest} | sleep: {sleep}s.')

                    time.sleep(sleep)
                else:
                    logger.warning(f'{short_address(str(sui_config.active_address))} | SCALLOP_DEPOSIT | '
                                   f'balance is not enough: {balance.float} $SUI. '
                                   f'minimum required: {round(amount_to_provide.int, 2)} $SUI.')
            else:
                logger.info(f'{short_address(str(sui_config.active_address))} | SCALLOP_DEPOSIT | '
                            f'enough provided liquidity: {provided_sui.float} $SUI.')
        else:
            logger.info(f'{short_address(str(sui_config.active_address))} | SCALLOP_DEPOSIT | '
                        f'enough provided liquidity: {provided_sui.float} $SUI.')

    except Exception as e:
        logger.exception(e)


def main_scallop_withdraw_sui(sui_config: SuiConfig):
    try:

        sui_reserve_coin_objects: SuiCoinObjects = SuiClient(config=sui_config).get_coin(
            coin_type=SuiString(SUI_RESERVE_COIN_TYPE),
            fetch_all=True).result_data

        amount_to_withdraw_int = sum(int(obj.balance) for obj in sui_reserve_coin_objects.data)
        amount_to_withdraw_float = round(amount_to_withdraw_int / 10 ** SUI_DENOMINATION, 2)

        if amount_to_withdraw_int:
            result = scallop_withdraw_sui_tx(sui_config=sui_config,
                                             amount=amount_to_withdraw_int,
                                             merge_list=sui_reserve_coin_objects.data)

            sleep = 0
            if result.reason:
                if result.digest:
                    sleep = random.randint(short_sleep_between_txs_in_range_in_sec[0],
                                           short_sleep_between_txs_in_range_in_sec[1])
                    logger.error(
                        f'{short_address(result.address)} | SCALLOP_WITHDRAW | {amount_to_withdraw_float} $SUI | '
                        f'digest: {result.digest} | '
                        f'reason: {result.reason} | sleep: {sleep}s.')
                else:
                    logger.error(
                        f'{short_address(result.address)} | SCALLOP_WITHDRAW | {amount_to_withdraw_float} $SUI | '
                        f'reason: {result.reason} | sleep: {sleep}s.')
            else:
                sleep = random.randint(short_sleep_between_txs_in_range_in_sec[0],
                                       short_sleep_between_txs_in_range_in_sec[1])
                logger.info(
                    f'{short_address(result.address)} | SCALLOP_WITHDRAW | {amount_to_withdraw_float} $SUI | '
                    f'digest: {result.digest} | '
                    f'sleep: {sleep}s.')
            time.sleep(sleep)
        else:
            logger.warning(f'{short_address(str(sui_config.active_address))} | '
                           f'nothing to withdraw.')

    except Exception as e:
        logger.exception(e)


def single_executor(sui_config: SuiConfig, withdraw: bool = False):
    if not start_threads_simultaneously:
        time.sleep(random.randint(1, 60))

    # merge_sui_coins(sui_config=sui_config)
    if withdraw:
        main_scallop_withdraw_sui(sui_config=sui_config)
    else:
        main_scallop_deposit_sui(sui_config=sui_config)


def main_scallop_executor(sui_configs: list[SuiConfig], withdraw: bool = False):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(single_executor, sui_configs, itertools.repeat(withdraw))
