import concurrent.futures
import itertools
import random
import time

from loguru import logger
from pysui.sui.sui_config import SuiConfig

from config import (short_sleep_between_txs_in_range_in_sec,
                    start_threads_simultaneously,
                    kriya_swap_value_in_sui_in_range)
from data import USDC_COIN_TYPE, USDC_DENOMINATION
from datatypes import SuiBalance, SuiTxResult
from utils import (short_address,
                   get_sui_balance,
                   kriya_swap_tx, get_minimum_usdc_to_receive)
from utils.coingecko import get_minimum_sui_to_receive
from utils.other_tools import get_sui_balance_object_from_range


def print_log_and_sleep(result: SuiTxResult, amount_to_swap: SuiBalance, token_from: str):
    sleep = 0
    if result.reason:
        if result.digest:
            sleep = random.randint(short_sleep_between_txs_in_range_in_sec[0],
                                   short_sleep_between_txs_in_range_in_sec[1])
            logger.error(
                f'{short_address(result.address)} | KRIYA_SWAP | {amount_to_swap.float} ${token_from} | '
                f'digest: {result.digest} | reason: {result.reason} | sleep: {sleep}s.')
        else:
            logger.error(
                f'{short_address(result.address)} | KRIYA_SWAP | {amount_to_swap.float} ${token_from} | '
                f'reason: {result.reason} | sleep: {sleep}s.')
    else:
        sleep = random.randint(short_sleep_between_txs_in_range_in_sec[0], short_sleep_between_txs_in_range_in_sec[1])
        logger.info(
            f'{short_address(result.address)} | KRIYA_SWAP | {amount_to_swap.float} ${token_from} | '
            f'digest: {result.digest} | sleep: {sleep}s.')
    time.sleep(sleep)


def main_kriya_swap(sui_config: SuiConfig, token_from: str, sui_price: float):
    try:
        amount_to_swap = SuiBalance(int=0, float=0)

        if token_from == 'USDC':
            balance = get_sui_balance(sui_config=sui_config, coin_type=USDC_COIN_TYPE, denomination=USDC_DENOMINATION)
        else:
            balance = get_sui_balance(sui_config=sui_config)

        if token_from == 'USDC':
            amount_to_swap = balance
        elif balance.float > kriya_swap_value_in_sui_in_range[1]:
            amount_to_swap = get_sui_balance_object_from_range(min_amount=kriya_swap_value_in_sui_in_range[0],
                                                               max_amount=kriya_swap_value_in_sui_in_range[1])
        else:
            logger.warning(f'{short_address(str(sui_config.active_address))} | KRIYA_SWAP | '
                           f'balance is not enough: {balance.float} ${token_from}. '
                           f'minimum required: {round(kriya_swap_value_in_sui_in_range[1], 2)} '
                           f'${token_from}.')

        if amount_to_swap.int:
            if token_from == 'USDC':
                minimum_received = get_minimum_sui_to_receive(usdc_amount=amount_to_swap, sui_price=sui_price)
            else:
                minimum_received = get_minimum_usdc_to_receive(sui_amount=amount_to_swap, sui_price=sui_price)

            result = kriya_swap_tx(sui_config=sui_config,
                                   amount=amount_to_swap.int,
                                   token_from=token_from,
                                   minimum_received=minimum_received)
            print_log_and_sleep(result=result, amount_to_swap=amount_to_swap, token_from=token_from)
        else:
            logger.warning(f'{short_address(str(sui_config.active_address))} | KRIYA_SWAP | '
                           f'${token_from} balance is zero.')

    except Exception as e:
        logger.exception(e)


def single_executor(sui_config: SuiConfig, token_from: str, sui_price: float):
    if not start_threads_simultaneously:
        time.sleep(random.randint(1, 60))

    # merge_sui_coins(sui_config=sui_config)
    main_kriya_swap(sui_config=sui_config, token_from=token_from, sui_price=sui_price)


def main_kriya_executor(sui_configs: list[SuiConfig], token_from: str, sui_price: float):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(single_executor, sui_configs, itertools.repeat(token_from), itertools.repeat(sui_price))
