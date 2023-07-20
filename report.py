import time

from loguru import logger

from data import VERSION
from utils import (add_logger,
                   read_mnemonics,
                   get_list_of_sui_configs,
                   print_rank_and_balance)

if __name__ == '__main__':
    add_logger(version=VERSION)
    try:
        mnemonics = read_mnemonics()
        sui_configs = get_list_of_sui_configs(mnemonics=mnemonics)

        for sui_config in sui_configs:
            print(sui_config.active_address)
        print()

        for num, sui_config in enumerate(sui_configs):
            print_rank_and_balance(num=num, sui_config=sui_config)
            time.sleep(1)

    except Exception as e:
        logger.exception(e)
    except KeyboardInterrupt:
        exit()
