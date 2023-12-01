import concurrent.futures
import random
import time

from config import (short_sleep_between_txs_in_range_in_sec,
                    start_threads_simultaneously)
from datatypes import SuiTransferConfig
from modules.claim import main_claim_reward
from modules.transfer import main_transfer_executor


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
