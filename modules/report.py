import time

from loguru import logger
from pysui import SuiConfig

from utils import (print_rank_and_balance)


def main_report_executor(sui_configs: list[SuiConfig]):
    for sui_config in sui_configs:
        print(sui_config.active_address)
    print()

    address_reports = []

    for num, sui_config in enumerate(sui_configs):
        address_reports.append(print_rank_and_balance(num=num, sui_config=sui_config))
        time.sleep(1)

    addresses_with_rank = 0
    for report in address_reports:
        if report:
            if report.rank < 999_999_999:
                addresses_with_rank += 1

    top500 = [rep for rep in address_reports if rep and (500 > rep.rank >= 1)]
    top1k = [rep for rep in address_reports if rep and (1_000 > rep.rank >= 501)]
    top5k = [rep for rep in address_reports if rep and (5_000 > rep.rank >= 1_001)]
    others = (addresses_with_rank - (len(top5k) + len(top500) + len(top1k)))

    logger.info(f'top500: {len(top500)}/{len(address_reports)}, '
                f'top1k: {len(top1k)}/{len(address_reports)}, '
                f'top5k: {len(top5k)}/{len(address_reports)}, '
                f'others: {others}.')

    top500_rewards = round(float(len(top500) * 2_500), 1)
    top1k_rewards = round(float(len(top1k) * 1_250), 1)
    top5k_rewards = round(float(len(top5k) * 156.25), 1)
    other_rewards = round(float(others * 12.5), 1)

    logger.info(f'expected rewards: {top500_rewards} + {top1k_rewards} + {top5k_rewards} + '
                f'{other_rewards} ~ {round(top500_rewards + top1k_rewards + top5k_rewards + other_rewards, 1)} $SUI.')
