import concurrent.futures
import random
import time

from loguru import logger
from pysui.sui.sui_config import SuiConfig

from config import (max_flip_count_per_session_in_range,
                    flip_bet_variants_in_sui,
                    sleep_range_between_txs_in_sec,
                    start_threads_simultaneously)
from data import VERSION
from datatypes import CoinflipSide
from utils import (add_logger,
                   read_mnemonics,
                   get_list_of_sui_configs,
                   short_address,
                   play_coinflip_tx,
                   get_associated_kiosk,
                   get_bullshark_id,
                   merge_sui_coins,
                   get_sui_balance,
                   print_rank_and_balance)


def main_play_game(sui_config: SuiConfig, associated_kiosk_addr: str, bullshark_addr: str):
    try:
        bet_amount = random.choice(flip_bet_variants_in_sui)
        balance = get_sui_balance(sui_config=sui_config)

        if balance.float > bet_amount:
            coinflip_side = random.choice(list(CoinflipSide))

            result = play_coinflip_tx(sui_config=sui_config,
                                      associated_kiosk_addr=associated_kiosk_addr,
                                      bullshark_addr=bullshark_addr,
                                      coinflip_side=coinflip_side,
                                      bet_amount=bet_amount)
            sleep = 0
            if result.reason:
                if result.digest:
                    sleep = random.randint(sleep_range_between_txs_in_sec[0], sleep_range_between_txs_in_sec[1])
                    logger.error(
                        f'{short_address(result.address)} | {coinflip_side.name} | digest: {result.digest} | '
                        f'reason: {result.reason} | sleep: {sleep}s.')
                else:
                    logger.error(
                        f'{short_address(result.address)} | {coinflip_side.name} | '
                        f'reason: {result.reason}.')
            else:
                sleep = random.randint(sleep_range_between_txs_in_sec[0], sleep_range_between_txs_in_sec[1])
                logger.info(f'{short_address(result.address)} | {coinflip_side.name} | digest: {result.digest} | '
                            f'sleep: {sleep}s.')

            time.sleep(sleep)
        else:
            logger.warning(f'{short_address(str(sui_config.active_address))} | '
                           f'balance is not enough: {balance.float} $SUI. '
                           f'minimum required: {bet_amount} $SUI.')
            return 'zero_balance'
    except Exception as e:
        logger.exception(e)


def single_executor(sui_config: SuiConfig):
    if not start_threads_simultaneously:
        time.sleep(random.randint(1, 60))

    merge_sui_coins(sui_config=sui_config)

    associated_kiosk_addr = get_associated_kiosk(address=str(sui_config.active_address))
    bullshark_addr = get_bullshark_id(kiosk_addr=associated_kiosk_addr).result.data[0].objectId

    flips_per_session = random.randint(max_flip_count_per_session_in_range[0], max_flip_count_per_session_in_range[1])
    broken = False
    for _ in range(flips_per_session):
        play_game_result = main_play_game(
            sui_config=sui_config,
            associated_kiosk_addr=associated_kiosk_addr,
            bullshark_addr=bullshark_addr
        )
        if play_game_result == 'zero_balance':
            broken = True
            break

    if not broken:
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
        for num, sui_config in enumerate(sui_configs):
            print_rank_and_balance(num=num, sui_config=sui_config)
            time.sleep(1)

        pool_executor(sui_configs=sui_configs)
    except Exception as e:
        logger.exception(e)
    except KeyboardInterrupt:
        exit()
