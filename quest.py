import time

from loguru import logger

from config import random_account_clusters
from data import VERSION
from modules.balance_checker import main_balance_executor
from modules.claim import main_claim_reward_executor
from modules.claim_x_transfer import main_claim_x_transfer_executor
from modules.generator import main_generator
from modules.kriya import main_kriya_executor
from modules.minter import main_minter_executor
from modules.navi import main_navi_executor
from modules.report import main_report_executor
from modules.scallop import main_scallop_executor
from modules.transfer import main_transfer_executor
from utils import (add_logger,
                   read_mnemonics,
                   get_list_of_sui_configs,
                   get_list_of_transfer_configs,
                   get_sui_price,
                   get_random_account_cluster)

if __name__ == '__main__':
    add_logger(version=VERSION)
    while True:
        try:
            mnemonics = read_mnemonics(path='data/mnemonic.txt')
            transfer_mnemonics = read_mnemonics(path='data/transfer.txt')

            sui_configs = get_list_of_sui_configs(mnemonics=mnemonics)
            random_sui_configs_cluster = get_random_account_cluster(sui_configs=sui_configs,
                                                                    randomize=random_account_clusters)

            # sui_price = get_sui_price()
            time.sleep(1)
            func = input('\n'
                         # '1. navi_deposit_borrow_repay();      # there is no withdraw module!\n'
                         # '2. scallop_deposit_liquidity();      # following the config\n'
                         # '3. scallop_withdraw_liquidity();     # 100% of provided liquidity\n'
                         # '4. kriya_swap(from_token=SUI);       # to $USDC only, following the config\n'
                         # '5. kriya_swap(from_token=USDC);      # to $SUI only, 100% of balance\n\n'
                         # '55. report(from="mnemonic.txt");\n'
                         
                         '56. transfer(from="transfer.txt");\n'
                         '57. reward_claim(from="mnemonic.txt");\n'
                         '58. claim_x_transfer(from="transfer.txt");\n\n'
                         
                         '61. capy_mint(from="mnemonic.txt");\n'
                         '62. balance_checker(from="mnemonic.txt");\n'
                         '63. mnemonic_generator(from="config.py");\n'
                         
                         # '77. 8192();              # deprecated\n'
                         # '78. coinflip();          # deprecated\n'
                         # '79. journey();           # deprecated\n\n'
                         'func number: ')

            if func == '1':
                print()
                main_navi_executor(sui_configs=random_sui_configs_cluster)
            if func == '2':
                print()
                main_scallop_executor(sui_configs=random_sui_configs_cluster)
            if func == '3':
                am_i_sure = input('are you sure that you wanna withdraw '
                                  'the whole provided liquidity from SCALLOP protocol (y, n): ')
                if am_i_sure == 'y':
                    print()
                    main_scallop_executor(sui_configs=random_sui_configs_cluster, withdraw=True)
            # if func == '4':
            #     print()
            #     main_kriya_executor(sui_configs=random_sui_configs_cluster, token_from='SUI', sui_price=sui_price)
            # if func == '5':
            #     print()
            #     main_kriya_executor(sui_configs=random_sui_configs_cluster, token_from='USDC', sui_price=sui_price)

            # if func == '55':
            #     print()
            #     main_report_executor(sui_configs=sui_configs)
            if func == '56':
                print()
                sui_transfer_configs = get_list_of_transfer_configs(mnemonics=transfer_mnemonics)
                for config in sui_transfer_configs:
                    main_transfer_executor(transfer_config=config)
            if func == '57':
                print()
                main_claim_reward_executor(sui_configs=sui_configs)
            if func == '58':
                print()
                sui_transfer_configs = get_list_of_transfer_configs(mnemonics=transfer_mnemonics)
                main_claim_x_transfer_executor(transfer_configs=sui_transfer_configs)

            if func == '61':
                print()
                main_minter_executor(sui_configs=sui_configs)
            if func == '62':
                print()
                main_balance_executor(sui_configs=sui_configs)
            if func == '63':
                print()
                main_generator()

            # if func == '77':
            #     print()
            #     main_8192_executor(sui_configs=sui_configs)
            # if func == '78':
            #     print()
            #     main_coinflip_executor(sui_configs=sui_configs)
            # if func == '79':
            #     print()
            #     main_journey_executor(sui_configs=sui_configs)

        except Exception as e:
            logger.exception(e)
        except KeyboardInterrupt:
            print()
            exit()
