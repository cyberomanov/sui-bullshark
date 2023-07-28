import time

from loguru import logger

from config import check_derivation_paths
from data import VERSION
from utils import (add_logger,
                   read_mnemonics,
                   get_list_of_sui_configs,
                   print_rank_and_balance)

if __name__ == '__main__':
    add_logger(version=VERSION)
    try:
        mnemonics = read_mnemonics()
        sui_configs = get_list_of_sui_configs(mnemonics=mnemonics, check_derivation_paths=check_derivation_paths)

        for sui_config in sui_configs:
            print(sui_config.active_address)
        print()

        address_reports = []
        top10k = []
        top5k = []

        for num, sui_config in enumerate(sui_configs):
            address_reports.append(print_rank_and_balance(num=num, sui_config=sui_config))
            time.sleep(1)

        top10k = [rep for rep in address_reports if (10_000 > rep.rank >= 5_000)]
        top5k = [rep for rep in address_reports if rep.rank < 5_000]

        logger.info(f'top10k: {len(top10k)}/{len(address_reports)}, top5k: {len(top5k)}/{len(address_reports)}, '
                    f'others: {len(address_reports) - (len(top10k) + len(top5k))}/{len(address_reports)}.')
        top10k_rewards = len(top10k) * 200
        top5k_rewards = len(top5k) * 100
        other_rewards = (len(address_reports) - (len(top10k) + len(top5k))) * 20

        logger.info(f'expected rewards: {top10k_rewards} + {top5k_rewards} + '
                    f'{other_rewards} ~ {top10k_rewards + top5k_rewards + other_rewards} $SUI.')

    except Exception as e:
        logger.exception(e)
    except KeyboardInterrupt:
        exit()
