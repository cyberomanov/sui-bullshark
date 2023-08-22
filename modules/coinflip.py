import concurrent.futures
import random
import time

from loguru import logger
from pysui.sui.sui_config import SuiConfig

from config import (max_flip_count_per_session_in_range,
                    flip_bet_variants_in_sui,
                    short_sleep_between_txs_in_range_in_sec,
                    start_threads_simultaneously)
from datatypes import CoinflipSide
from utils import (short_address,
                   play_coinflip_tx,
                   get_associated_kiosk,
                   get_bullshark_id,
                   merge_sui_coins,
                   get_sui_balance)


def main_play_game(sui_config: SuiConfig, associated_kiosk_addr: str, bullshark_addr: str):
    try:
        merge_sui_coins(sui_config=sui_config)
        balance = get_sui_balance(sui_config=sui_config)

        bet_amount = random.choice(flip_bet_variants_in_sui)
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
                    sleep = random.randint(short_sleep_between_txs_in_range_in_sec[0],
                                           short_sleep_between_txs_in_range_in_sec[1])
                    logger.error(
                        f'{short_address(result.address)} | {coinflip_side.name} | digest: {result.digest} | '
                        f'reason: {result.reason} | sleep: {sleep}s.')
                else:
                    logger.error(
                        f'{short_address(result.address)} | {coinflip_side.name} | '
                        f'reason: {result.reason}.')
            else:
                sleep = random.randint(short_sleep_between_txs_in_range_in_sec[0],
                                       short_sleep_between_txs_in_range_in_sec[1])
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

    associated_kiosk_addr = get_associated_kiosk(address=str(sui_config.active_address))
    kiosk_dynamic_fields = get_bullshark_id(kiosk_addr=associated_kiosk_addr).result.data

    bullshark_addr = None
    for field in kiosk_dynamic_fields:
        if 'bullshark' in str(field.objectType).lower():
            bullshark_addr = field.objectId

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


def main_coinflip_executor(sui_configs: list[SuiConfig]):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(single_executor, sui_configs)
