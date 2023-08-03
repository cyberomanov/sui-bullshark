import random
import time

from loguru import logger

from config import (start_threads_simultaneously,
                    check_derivation_paths,
                    value_to_leave_in_sui, sleep_range_between_txs_in_sec)
from data import VERSION
from datatypes import SuiTransferConfig
from utils import (add_logger,
                   read_mnemonics,
                   short_address,
                   merge_sui_coins,
                   get_sui_balance,
                   get_list_of_transfer_configs,
                   get_balance_to_transfer,
                   transfer_sui_tx)


def main_transfer(transfer_config: SuiTransferConfig):
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
                if balance_to_transfer.float > 0.15:
                    at_least_one_swap = True

                    result = transfer_sui_tx(sui_config=sui_config, recipient=recipient_address, amount=balance_to_transfer)

                    sleep = 0
                    if result.reason:
                        if result.digest:
                            sleep = random.randint(sleep_range_between_txs_in_sec[0], sleep_range_between_txs_in_sec[1])
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
                        sleep = random.randint(sleep_range_between_txs_in_sec[0], sleep_range_between_txs_in_sec[1])
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
                            f'minimum value to leave: {round(value_to_leave_in_float + 0.15, 2)} $SUI.')
                    break
            else:
                if not at_least_one_swap:
                    logger.warning(f'{short_address(str(sui_config.active_address))} -> {short_address(recipient_address)} | '
                                   f'balance is not enough: {balance.float} $SUI. '
                                   f'minimum value to leave: {value_to_leave_in_float} $SUI.')
                break

    except:
        logger.exception(e)


if __name__ == '__main__':
    add_logger(version=VERSION)
    try:
        mnemonics = read_mnemonics(path='data/transfer.txt')
        sui_configs = get_list_of_transfer_configs(mnemonics=mnemonics, check_derivation_paths=check_derivation_paths)
        for config in sui_configs:
            main_transfer(transfer_config=config)
    except Exception as e:
        logger.exception(e)
    except KeyboardInterrupt:
        exit()
