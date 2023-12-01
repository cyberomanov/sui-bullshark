import concurrent.futures
import random
import time

from loguru import logger
from pysui.sui.sui_config import SuiConfig

from config import (short_sleep_between_txs_in_range_in_sec,
                    start_threads_simultaneously)
from utils import (short_address,
                   claim_reward,
                   get_signature)
from utils.other_tools import encode_signature


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
                logger.success(
                    f'{short_address(result.address)} | REWARD_CLAIM | '
                    f'digest: {result.digest} | sleep: {sleep}s.')
        else:
            logger.warning(
                    f'{short_address(str(sui_config.active_address))} | REWARD_CLAIM | '
                    f'no rewards.')

    except Exception as e:
        logger.exception(e)


def single_executor(sui_config: SuiConfig):
    if not start_threads_simultaneously:
        time.sleep(random.randint(1, 60))

    main_claim_reward(sui_config=sui_config)


def main_claim_reward_executor(sui_configs: list[SuiConfig]):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(single_executor, sui_configs)
