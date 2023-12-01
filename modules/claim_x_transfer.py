import concurrent.futures
import random
import time

from loguru import logger
from pysui.sui.sui_config import SuiConfig

from config import (short_sleep_between_txs_in_range_in_sec,
                    start_threads_simultaneously, value_to_leave_in_sui)
from datatypes import SuiTransferConfig
from utils import (short_address,
                   claim_reward,
                   get_signature, merge_sui_coins, get_sui_balance, transfer_sui_tx)
from utils.other_tools import encode_signature, get_balance_to_transfer


def main_claim_reward(sui_config: SuiConfig):
    try:
        signature_response = get_signature(address=str(sui_config.active_address), quest_id=3)
        if signature_response:
            signature_bytes = encode_signature(signature=signature_response.result.data.signature)

            result = claim_reward(sui_config=sui_config, signature=signature_bytes)

            sleep = 0
            if result.reason:
                if result.digest:
                    sleep = random.randint(short_sleep_between_txs_in_range_in_sec[0],
                                           short_sleep_between_txs_in_range_in_sec[1])
                    logger.error(
                        f'{short_address(result.address)} | REWARD_CLAIM | '
                        f'digest: {result.digest} | reason: {result.reason} | sleep: {sleep}s.')
                else:
                    if 'claim at offset 24' in result.reason:
                        logger.info(
                            f'{short_address(result.address)} | REWARD_CLAIM | already claimed.')
                    else:
                        logger.error(
                            f'{short_address(result.address)} | REWARD_CLAIM | '
                            f'reason: {result.reason} | sleep: {sleep}s.')
            else:
                sleep = random.randint(short_sleep_between_txs_in_range_in_sec[0],
                                       short_sleep_between_txs_in_range_in_sec[1])
                logger.info(
                    f'{short_address(result.address)} | REWARD_CLAIM | '
                    f'digest: {result.digest} | sleep: {sleep}s.')
        else:
            logger.warning(
                f'{short_address(str(sui_config.active_address))} | REWARD_CLAIM | '
                f'no rewards.')

    except Exception as e:
        logger.exception(e)


def main_transfer_executor(transfer_config: SuiTransferConfig):
    if not start_threads_simultaneously:
        time.sleep(random.randint(1, 60))

    sui_config = transfer_config.config
    recipient_address = transfer_config.address

    try:
        merge_sui_coins(sui_config=sui_config)

        at_least_one_swap = False
        while True:
            balance = get_sui_balance(sui_config=sui_config)
            value_to_leave_in_float = round(random.uniform(value_to_leave_in_sui[0], value_to_leave_in_sui[1]),
                                            random.randint(2, 4))
            if balance.float > value_to_leave_in_float:
                balance_to_transfer = get_balance_to_transfer(balance=balance,
                                                              value_to_leave_in_sui=value_to_leave_in_float)

                if balance_to_transfer.float > 0.1:
                    at_least_one_swap = True

                    result = transfer_sui_tx(sui_config=sui_config, recipient=recipient_address,
                                             amount=balance_to_transfer)

                    sleep = 0
                    if result.reason:
                        if result.digest:
                            sleep = random.randint(short_sleep_between_txs_in_range_in_sec[0],
                                                   short_sleep_between_txs_in_range_in_sec[1])
                            logger.error(
                                f'{short_address(result.address)} -> {short_address(recipient_address)} | '
                                f'transfer: {balance_to_transfer.float} $SUI | digest: {result.digest} | '
                                f'reason: {result.reason} | sleep: {sleep}s.')
                        else:
                            logger.error(
                                f'{short_address(result.address)} -> {short_address(recipient_address)} | '
                                f'transfer: {balance_to_transfer.float} $SUI | '
                                f'reason: {result.reason}.')
                    else:
                        sleep = random.randint(short_sleep_between_txs_in_range_in_sec[0],
                                               short_sleep_between_txs_in_range_in_sec[1])
                        logger.info(
                            f'{short_address(result.address)} -> {short_address(recipient_address)} | '
                            f'transfer: {balance_to_transfer.float} $SUI | digest: {result.digest} | '
                            f'sleep: {sleep}s.')

                    time.sleep(sleep)
                else:
                    if not at_least_one_swap:
                        logger.warning(
                            f'{short_address(str(sui_config.active_address))} -> {short_address(recipient_address)} | '
                            f'balance is not enough: {balance.float} $SUI. '
                            f'minimum value to leave: {round(value_to_leave_in_float + 0.1, 2)} $SUI.')
                    break
            else:
                if not at_least_one_swap:
                    logger.warning(
                        f'{short_address(str(sui_config.active_address))} -> {short_address(recipient_address)} | '
                        f'balance is not enough: {balance.float} $SUI. '
                        f'minimum value to leave: {value_to_leave_in_float} $SUI.')
                break

    except Exception as e:
        logger.exception(e)


def single_executor(transfer_config: SuiTransferConfig):
    if not start_threads_simultaneously:
        time.sleep(random.randint(1, 60))

    main_claim_reward(sui_config=transfer_config.config)
    time.sleep(random.randint(short_sleep_between_txs_in_range_in_sec[0],
                              short_sleep_between_txs_in_range_in_sec[1]))
    main_transfer_executor(transfer_config=transfer_config)


def main_claim_x_transfer_executor(transfer_configs: [SuiTransferConfig]):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(single_executor, transfer_configs)
