import concurrent.futures
import random
import time

from loguru import logger
from pysui.sui.sui_config import SuiConfig

from config import (total_max_8192_games_per_address_in_range,
                    sleep_range_between_txs_in_sec,
                    sleep_range_between_games_in_sec,
                    start_threads_simultaneously)
from data import VERSION, SUI_NATIVE_DENOMINATION, GAME_8192_MINT_PRICE
from datatypes import Arrow
from utils import (add_logger,
                   read_mnemonics,
                   get_list_of_sui_configs,
                   execute_move_tx,
                   mint_game_tx,
                   short_address,
                   get_game_items_count,
                   get_active_game_ids,
                   get_sui_object_response,
                   merge_sui_coins,
                   get_sui_balance,
                   print_rank_and_balance)


def main_play_game(sui_config: SuiConfig, game_id: str):
    game_over = False

    while not game_over:
        try:
            failed_arrow = True
            set_of_failed_arrows = set()

            while not game_over and failed_arrow:
                move = random.choice(list(set(Arrow) - set_of_failed_arrows))

                result = execute_move_tx(sui_config=sui_config, game_id=game_id, move=move)
                if result.reason:
                    logger.info(f'{short_address(result.address)} | {result.move.name:>5} | '
                                f'reason: direction is blocked.')

                    if get_sui_object_response(object_id=game_id).result.data.content.fields.game_over:
                        logger.warning(f'{short_address(result.address)} | game_id: {game_id} | reason: game is over.')
                        game_over = True
                    else:
                        set_of_failed_arrows.add(result.move)
                else:
                    failed_arrow = False
                    sleep = random.randint(sleep_range_between_txs_in_sec[0], sleep_range_between_txs_in_sec[1])
                    logger.info(f'{short_address(result.address)} | {result.move.name:>5} | '
                                f'digest: {result.digest} | sleep: {sleep}s.')
                    time.sleep(sleep)
        except:
            pass


def main_mint_game(sui_config: SuiConfig):
    result = mint_game_tx(sui_config=sui_config)
    if result.reason:
        logger.warning(f'{short_address(result.address)} |  MINT | digest: {result.digest} | reason: {result.reason}.')
    else:
        logger.info(f'{short_address(result.address)} |  MINT | digest: {result.digest}')


def single_executor(sui_config: SuiConfig):
    if not start_threads_simultaneously:
        time.sleep(random.randint(1, 60))

    merge_sui_coins(sui_config=sui_config)

    played_games = get_game_items_count(address=str(sui_config.active_address))
    games_per_address = random.randint(total_max_8192_games_per_address_in_range[0],
                                       total_max_8192_games_per_address_in_range[1])

    while played_games < games_per_address:
        active_game_8192_ids = get_active_game_ids(address=str(sui_config.active_address))

        if not active_game_8192_ids:
            balance = get_sui_balance(sui_config=sui_config)
            if balance.float > 0.2:
                main_mint_game(sui_config=sui_config)
                time.sleep(random.randint(sleep_range_between_txs_in_sec[0], sleep_range_between_txs_in_sec[1]))

            else:
                logger.info(f'{short_address(str(sui_config.active_address))} | '
                            f'balance is not enough: {balance.float} $SUI. '
                            f'minimum required: {round(GAME_8192_MINT_PRICE / 10 ** SUI_NATIVE_DENOMINATION, 2)} $SUI.')
                break

        active_game_8192_ids = get_active_game_ids(address=str(sui_config.active_address))
        if len(active_game_8192_ids):
            random_game = random.choice(active_game_8192_ids)
            logger.info(f'{short_address(str(sui_config.active_address))} | current_game_id: {random_game}')
            main_play_game(sui_config=sui_config, game_id=random_game)

            sleep = random.randint(sleep_range_between_games_in_sec[0], sleep_range_between_games_in_sec[1])
            logger.info(f'{short_address(str(sui_config.active_address))} | sleep: {sleep}s.')
            time.sleep(sleep)

    logger.success(f'{short_address(str(sui_config.active_address))} | has played {played_games} games.')


def pool_executor(sui_configs: list[SuiConfig]):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(single_executor, sui_configs)


if __name__ == '__main__':
    add_logger(version=VERSION)
    try:
        mnemonics = read_mnemonics()
        sui_configs = get_list_of_sui_configs(mnemonics=mnemonics)

        logger.info('loaded addresses for 8192 game:')
        for num, sui_config in enumerate(sui_configs):
            print_rank_and_balance(num=num, sui_config=sui_config)
            time.sleep(1)

        pool_executor(sui_configs=sui_configs)
    except Exception as e:
        logger.exception(e)
    except KeyboardInterrupt:
        exit()
